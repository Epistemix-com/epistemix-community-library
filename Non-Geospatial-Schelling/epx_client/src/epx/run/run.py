import os
import logging
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel

from epx.config import get_cache_dir
from epx.run.fs import FileFinderFactory
from epx.run.status import RunStatus, RunStatusFactory
from epx.run.results import RunResults, RunResultsFactory
from epx.run.exec.compat import (
    adapt_params_for_fred_version,
    fred_major_version,
    rescale_seed_to_run_number,
)
from epx.run.exec import (
    RunExecuteStrategy,
    RunExecuteCloudStrategy,
    RunParameters,
    RunParametersModel,
)

logger = logging.getLogger(__name__)


class _RunModel(BaseModel):
    params: RunParametersModel
    output_dir: Union[Path, str]
    size: str
    fred_version: str

    @staticmethod
    def from_run(run: "Run") -> "_RunModel":
        return _RunModel(
            params=RunParametersModel.from_run_parameters(run.params),
            output_dir=run.output_dir,
            size=run.size,
            fred_version=run.fred_version,
        )

    def as_run(self) -> "Run":
        return Run(
            params=self.params.as_run_parameters(),
            output_dir=self.output_dir,
            size=self.size,
            fred_version=self.fred_version,
        )


class Run:
    """Client interface for manipulating individual simulation runs.

    Parameters
    ----------
    params : RunParameters
        Parameters to be passed to FRED configuring the run.
    output_dir : Union[Path, str]
        Directory in the user's environment to write run results to.
    size : str, optional
        Size of cloud instance to use for the run. Defaults to ``hot``.
    fred_version : str, optional
        FRED version to use for the run. Defaults to ``latest``.

    Attributes
    ----------
    params : RunParameters
        Parameters to be passed to FRED configuring the run.
    output_dir : Path
        Directory in the user's environment to write run results to.
    size : str, optional
        Size of cloud instance to use for the run.
    fred_version : str, optional
        FRED version to use for the run.
    """

    def __init__(
        self,
        params: RunParameters,
        output_dir: Union[Path, str],
        size: str = "hot",
        fred_version: str = "latest",
    ):
        self.params = params
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.size = size
        self.fred_version = fred_version
        self._exec_strategy: RunExecuteStrategy = RunExecuteCloudStrategy(
            adapt_params_for_fred_version(self.params, fred_version),
            self.output_dir,
            self.size,
            self.fred_version,
        )

    @classmethod
    def from_output_dir(cls, output_dir: Union[Path, str]) -> "Run":
        """Construct a ``Run`` object from a previously executed simulation run.

        Uses data from the ``output_dir`` to obtain a Run object.

        Parameters
        ----------
        output_dir : Union[Path, str]
            The output directory used for the previously executed run.
        """
        try:
            run_config_file = cls._cache_dir(Path(output_dir)) / "run.json"
            with open(run_config_file, "r") as f:
                return _RunModel.model_validate_json(f.read()).as_run()
        except FileNotFoundError as e:
            logger.error(e)
            raise
        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def _cache_dir(output_dir: Path) -> Path:
        """Construct path to the directory in which to store cached data for the
        run.

        The absolute path to the output directory is the unique name for the
        run. Cached data for each run is stored under
        ``~/.epx_client/runs/<run_name>``.

        Parameters
        ----------
        output_dir : Path
            Directory in the user's environment to write run results to.

        Notes
        -----
        We considered using ``output_dir/epx_client`` as the location for the
        run cache. However, currently FRED Cloud silently fails if the specified
        output directory already contains data when the run request is made.
        Storing run cache data separately in ``~/.epx_client/runs/`` avoids this
        problem.
        """
        run_name = str(output_dir.resolve())[1:]
        return get_cache_dir() / "runs" / Path(run_name)

    def execute(self) -> None:
        """Execute the simulation run."""
        self._verify_output_dir_empty()
        self._init_cache()
        self._write_run_config()
        return self._exec_strategy.execute()

    def _verify_output_dir_empty(self) -> None:
        """Ensure that ``output_dir`` does not contain any regular files.

        If ``output_dir`` does contain regular files, this is interpreted as
        meaning that a run of the given name already exists.

        Raises
        ------
        RunExistsError
            If the specified output_dir already contains regular files.
        """
        if self.output_dir.is_dir():
            # output_dir exists
            if any(self.output_dir.iterdir()):
                # output_dir contains files
                raise RunExistsError(self.output_dir)

    def _init_cache(self) -> None:
        self._cache_dir(self.output_dir).mkdir(exist_ok=True, parents=True)

    def _write_run_config(self) -> None:
        with open(self._cache_dir(self.output_dir) / "run.json", "w") as f:
            f.write(_RunModel.from_run(self).model_dump_json())

    def delete(self, interactive=True) -> None:
        """Delete all results data for the run.

        Users should be careful to ensure that the ``output_dir`` specified in
        the constructor is indeed the targeted run directory. This is a
        destructive operation and should be used with care. E.g. if
        ``output_dir = Path('/')`` this would cause the deletion of all files
        on the system that the user has write permissions for.

        Parameters
        ----------
        interactive : bool, optional
            Whether or not the ``delete`` command should be run interactively.
            When ``True`` (the default), the user will be prompted to confirm
            the deletion of all files in the run directory. When ``False``, no
            confirmation prompt will be given. The latter option is provided to
            support programmatic usage, e.g. to delete the data for all runs in
            a collection of runs.
        """

        def confirm(output_dir: Path) -> bool:
            answer = input(f"Delete contents of {output_dir}? [y/N]")
            if answer.lower() in ["y", "yes"]:
                return True
            else:
                return False

        def proceed():
            for root, dirs, files in os.walk(self.output_dir, topdown=False):
                for name in files:
                    (Path(root) / name).unlink()
                for name in dirs:
                    (Path(root) / name).rmdir()
            self.output_dir.rmdir()

        if not interactive or confirm(self.output_dir):
            proceed()

    @property
    def status(self) -> RunStatus:
        """Status object for the run."""
        if fred_major_version(self.fred_version) < 11:
            run_number = rescale_seed_to_run_number(self.params.seed)
        else:
            run_number = None
        return RunStatusFactory(
            FileFinderFactory(self.output_dir, run_number).build()
        ).build()

    @property
    def results(self) -> Optional[RunResults]:
        """RunResults, optional: Results object for the run. If the results
        directory has not been populated yet, returns ``None``.
        """
        if str(self.status) != "DONE":
            return None
        if fred_major_version(self.fred_version) < 11:
            run_number = rescale_seed_to_run_number(self.params.seed)
        else:
            run_number = None
        return RunResultsFactory(
            FileFinderFactory(self.output_dir, run_number).build()
        ).build()

    def __repr__(self) -> str:
        return (
            f"Run("
            f"params={self.params}, "
            f"output_dir={self.output_dir}, "
            f"size={self.size}, "
            f"fred_version={self.fred_version}"
            f")"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Run):
            return False
        if (
            (self.params == other.params)
            and (self.output_dir == other.output_dir)
            and (self.size == other.size)
            and (self.fred_version == other.fred_version)
        ):
            return True
        return False


class RunExistsError(Exception):
    """Thrown when user specifies an output_dir that already contains data."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        super().__init__(
            f"Run data already exists in output_dir: {self.output_dir}. "
            "Call Run.delete to delete this data and reuse output_dir."
        )
