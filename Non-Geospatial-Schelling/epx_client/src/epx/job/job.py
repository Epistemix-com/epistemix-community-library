"""Functionality for configuring and running collections runs (called jobs)."""

from dataclasses import dataclass
from datetime import date
from itertools import chain, islice, product, takewhile, repeat
import logging
from pathlib import Path
from typing import Any, Iterable, Optional, TypeAlias, TypeVar, Union

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from pydantic import BaseModel

from epx.config import get_cache_dir, default_results_dir
from epx.random import random_seed
from epx.synthpop import SynthPop, SynthPopModel
from epx.run.run import Run, RunParameters
from epx.job.results import JobResults
from epx.job.status import JobStatus

logger = logging.getLogger(__name__)


ModelParams: TypeAlias = dict[str, Union[float, str]]
T = TypeVar("T")


@dataclass
class ModelConfig:
    """Configuration for a model run, including multiple realizations if
    applicable.

    Attributes
    ----------
    synth_pop : SynthPop
        Synthetic population to use for the run.
    start_date : Union[date, str], optional
        Simulation start date. If a ``str`` is given, should be in ISO 8601
        format, i.e. ``YYYY-MM-DD``.
    end_date : Union[date, str], optional
        Simulation end date. If a ``str`` is given, should be in ISO 8601
        format, i.e. ``YYYY-MM-DD``.
    model_params : ModelParams, optional
        Dictionary where the keys are model variable names and the values are
        the corresponding numeric or string values.
    seed : Union[int, Iterable[int]], optional
        Random number seeds for the configured runs. If ``None`` (the default),
        random seeds will be generated as required. If ``n_reps>1`` and a
        non-null value is given, this must be an iterable of length ``n_reps``.
    n_reps : int, optional
        Number of realizations of the model to run. By default, 1.
    """

    synth_pop: SynthPop
    start_date: Optional[Union[date, str]] = None
    end_date: Optional[Union[date, str]] = None
    model_params: Optional[ModelParams] = None
    seed: Optional[Union[int, Iterable[int]]] = None
    n_reps: int = 1

    def __post_init__(self):
        self.seed = self._normalize_seed(self.seed, self.n_reps)

    @staticmethod
    def _normalize_seed(
        seed: Optional[Union[int, Iterable[int]]], n_reps: int
    ) -> Optional[Union[int, Iterable[int]]]:
        """Normalize and validate given seed value(s).

        Ensures that ``seed`` is compatible with the specified number of
        repetitions, ``n_reps``.
        """
        norm_seed: Optional[Union[int, Iterable[int]]]
        if seed is None:
            norm_seed = None
        else:
            if isinstance(seed, int):
                if n_reps == 1:
                    norm_seed = seed
                else:
                    raise IndexError(f"n_reps={n_reps} but a single seed given")
            elif isinstance(seed, Iterable):
                tuple_seeds = tuple(seed)
                if n_reps != len(tuple_seeds):
                    raise IndexError(
                        f"n_reps={n_reps} but {len(tuple_seeds)} seeds given"
                    )
                if len(tuple_seeds) == 1:
                    norm_seed = tuple_seeds[0]
                else:
                    norm_seed = tuple_seeds
        return norm_seed


class _ModelConfigModel(BaseModel):
    synth_pop: SynthPopModel
    start_date: Optional[Union[date, str]] = None
    end_date: Optional[Union[date, str]] = None
    params: Optional[ModelParams] = None
    seed: Optional[Union[int, tuple[int, ...]]] = None
    n_reps: int = 1

    @staticmethod
    def from_model_config(model_config: "ModelConfig") -> "_ModelConfigModel":
        return _ModelConfigModel(
            synth_pop=SynthPopModel.from_synth_pop(model_config.synth_pop),
            start_date=model_config.start_date,
            end_date=model_config.end_date,
            params=model_config.model_params,
            seed=model_config.seed,
            n_reps=model_config.n_reps,
        )

    def as_model_config(self) -> "ModelConfig":
        return ModelConfig(
            synth_pop=self.synth_pop.as_synth_pop(),
            start_date=self.start_date,
            end_date=self.end_date,
            model_params=self.params,
            seed=self.seed,
            n_reps=self.n_reps,
        )


class ModelConfigSweep:
    """Sweep over parameters for a given model.

    The set of model configurations represented by ``ModelConfigSweep`` objects
    constructed by taking the cartesian product of the given sequences of input
    parameters (see Examples).

    Parameters
    ----------
    synth_pop : Iterable[SynthPop]
        Sequence of populations to use for the runs.
    start_date : Iterable[Union[date, str]], optional
        Sequence of simulation start dates to use for the runs. If start dates
        are given as ``str``, they should be in ISO 8601 format, i.e.
        ``YYYY-MM-DD``.
    end_date : Iterable[Union[date, str]], optional
        Sequence of simulation end dates to use for the runs. If end dates
        are given as ``str``, they should be in ISO 8601 format, i.e.
        ``YYYY-MM-DD``.
    model_params : Iterable[ModelParams], optional
        Sequence of model parameters to use for the runs. Each item should be
        a dictionary where the keys are model variable names and the values are
        the corresponding numeric or string values. By default ``None``.
    seed : Union[Iterable[int], int], optional
        If an iterable is given, the number of elements must equal the number of
        combinations of values in the ``synth_pop``, ``start_date``,
        ``end_date``, and ``model_params`` iterables **multiplied** by
        ``n_reps``. If a single value is given, this is used as the 'meta seed'
        to pseudo-randomly generate seeds for each of the runs. If ``None`` is
        given, seeds for each run are generated using unpredictable entropy from
        the OS (see `docs`_ for ``numpy.random.default_rng``).
    n_reps : int, optional
        Number of realizations of each model configuration. By default, 1.

    .. _docs: https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng  # noqa: E501

    Examples
    --------
    >>> sweep = ModelConfigSweep(
    ...     synth_pop=[SynthPop("US_2010.v5", ["Location1", "Location2"])],
    ...     start_date=["2024-01-01"],
    ...     end_date=["2024-01-31", "2024-02-29"],
    ... )
    >>> model_configs = list(sweep)
    >>> print(len(model_configs))
    2
    >>> print(model_configs[0].end_date)
    2024-01-31
    >>> print(model_configs[1].end_date)
    2024-02-29
    """

    def __init__(
        self,
        synth_pop: Iterable[SynthPop],
        start_date: Optional[Iterable[Union[date, str]]],
        end_date: Optional[Iterable[Union[date, str]]],
        model_params: Optional[Iterable[ModelParams]] = None,
        seed: Optional[Union[Iterable[int], int]] = None,
        n_reps: int = 1,
    ):
        self.synth_pop = synth_pop
        self.start_date = self._normalize_optional_param(start_date)
        self.end_date = self._normalize_optional_param(end_date)
        self.model_params = self._normalize_optional_param(model_params)
        self.seed = seed
        self.n_reps = n_reps
        self._configs = self._get_configs()

    @staticmethod
    def _normalize_optional_param(
        param: Optional[Iterable[T]],
    ) -> Iterable[Optional[T]]:
        """Ensure that ``param`` is an iterable of ``T``.

        Converting from Optional[Iterable[T]] to an Iterable[Optional[T]]
        allows us to pass the return value of this function to ``product``.
        Without this normalization, when ``None`` (rather than ``[None]``) was
        passed to ``product`` the returned iterable would be empty.
        """
        if param is None:
            return [None]
        return [x for x in param]

    def _get_configs(self) -> list[ModelConfig]:
        """Broadcast parameter combinations into a list of ModelConfigs."""
        configs = [
            x
            for x in product(
                self.synth_pop,
                self.start_date,
                self.end_date,
                self.model_params,
            )
        ]
        seeds: list[int]
        if self.seed is None:
            seeds = [random_seed() for _ in range(len(configs) * self.n_reps)]
        elif isinstance(self.seed, int):
            seeds = [random_seed(self.seed) for _ in range(len(configs) * self.n_reps)]
        else:
            try:
                iter(self.seed)
                seeds = [x for x in self.seed]
                if (n_seeds := len(seeds)) != (n_configs := len(configs) * self.n_reps):
                    raise IndexError(
                        f"Received {n_configs} configs but {n_seeds} seeds"
                    )
            except TypeError:
                raise ValueError("Invalid seed value")

        configs_with_seeds = zip(configs, self._split_every(self.n_reps, seeds))
        return [
            ModelConfig(
                synth_pop, start_date, end_date, model_params, seed, self.n_reps
            )
            for (
                synth_pop,
                start_date,
                end_date,
                model_params,
            ), seed in configs_with_seeds
        ]

    @staticmethod
    def _split_every(n: int, iterable: Iterable[Any]) -> Iterable[list[Any]]:
        """Slice an iterable into chunks of n elements.

        Parameters
        ----------
        n : int
            Number of elements in each chunk.
        iterable : Iterable
            Iterable to slice.

        Returns
        -------
        Iterator
            Iterator over the chunks of the input iterable.
        """
        iterator = iter(iterable)
        return takewhile(bool, (list(islice(iterator, n)) for _ in repeat(None)))

    def __iter__(self):
        return (x for x in self._configs)

    def __repr__(self) -> str:
        return (
            f"ModelConfigSweep("
            f"synth_pop={self.synth_pop}, "
            f"start_date={self.start_date}, "
            f"end_date={self.end_date}, "
            f"model_params={self.model_params}, "
            f"seed={self.seed}, "
            f"n_reps={self.n_reps}"
            f")"
        )


class _JobModel(BaseModel):
    program: Path
    config: list[_ModelConfigModel]
    key: str
    size: str = "hot"
    fred_version: str = "latest"
    n: int = 1
    results_dir: Optional[Path] = None

    @staticmethod
    def from_job(job: "Job") -> "_JobModel":
        return _JobModel(
            program=job.program,
            config=[_ModelConfigModel.from_model_config(x) for x in job.config],
            key=job.key,
            size=job.size,
            fred_version=job.fred_version,
            results_dir=job.results_dir,
        )

    def as_job(self) -> "Job":
        return Job(
            program=self.program,
            config=[x.as_model_config() for x in self.config],
            key=self.key,
            size=self.size,
            fred_version=self.fred_version,
            results_dir=self.results_dir,
        )


class Job:
    def __init__(
        self,
        program: Union[Path, str],
        config: Iterable[ModelConfig],
        key: str,
        size: str = "hot",
        fred_version="latest",
        results_dir: Optional[Union[Path, str]] = None,
    ):
        """Client interface for configuring and running collections of
        simulation runs.

        Parameters
        ----------
        program : Union[Path, str]
            Path to the FRED entrypoint file.
        config : Iterable[ModelConfig]
            Set of model run configurations to execute.
        key : str
            Unique identifier for the job.
        size : str, optional
            Instance size to use for each run in the job, by default "hot".
        fred_version : str, optional
            FRED Simulation Engine version to use for each run in the job,
            by default "latest".
        results_dir : Optional[Union[Path, str]], optional
            Root results directory to use to store simulation results. By
            default ``None``, causing results to be stored in the default
            directory, ``~/results``.
        """
        self.program = Path(program)
        self.config = list(config)
        self.key = key
        self.size = size
        self.fred_version = fred_version
        self.results_dir = (
            Path(results_dir).expanduser().resolve()
            if results_dir
            else default_results_dir()
        )
        self._runs = self._build_runs(
            self.program,
            self.config,
            self.results_dir,
            self.key,
            self.size,
            self.fred_version,
        )

    @classmethod
    def _build_runs(
        cls,
        program: Path,
        config: Iterable[ModelConfig],
        results_dir: Path,
        key: str,
        size: str,
        fred_version: str,
    ) -> tuple[Run, ...]:
        def disaggregate_model_config(model_config: ModelConfig) -> list[ModelConfig]:
            """Convert model config representing multiple realizations into a
            list of model configs each representing a single realization.
            """
            if model_config.n_reps == 1:
                return [model_config]
            if isinstance(model_config.seed, Iterable):
                seeds: list[Optional[int]] = list(model_config.seed)
            else:
                seeds = [None for _ in range(model_config.n_reps)]
            return [
                ModelConfig(
                    synth_pop=model_config.synth_pop,
                    start_date=model_config.start_date,
                    end_date=model_config.end_date,
                    model_params=model_config.model_params,
                    seed=seeds[i],
                    n_reps=1,
                )
                for i, _ in enumerate(range(model_config.n_reps))
            ]

        def validate_singular_seed(
            seed: Optional[Union[int, Iterable[int]]]
        ) -> Optional[int]:
            if seed is not None and not isinstance(seed, int):
                raise ValueError("Seed must be an integer if n_reps=1")
            return seed

        job_dir = cls._get_job_output_dir(results_dir, key)
        job_dir.mkdir(parents=True, exist_ok=True)
        return tuple(
            Run(
                params=RunParameters(
                    program=program,
                    synth_pop=model_config.synth_pop,
                    start_date=model_config.start_date,
                    end_date=model_config.end_date,
                    model_params=model_config.model_params,
                    seed=validate_singular_seed(model_config.seed),
                ),
                output_dir=job_dir / str(run_id),
                size=size,
                fred_version=fred_version,
            )
            for run_id, model_config in enumerate(
                chain(
                    *[
                        disaggregate_model_config(model_config)
                        for model_config in config
                    ]
                )
            )
        )

    @staticmethod
    def _get_job_output_dir(results_dir: Path, key: str) -> Path:
        return results_dir / key

    @classmethod
    def from_key(cls, job_key: str) -> "Job":
        """Retrieve a Job object from a job key.

        Useful if one knows the key for a job but e.g. hadn't
        assigned the return value of `run_job` to a variable.

        Parameters
        ----------
        job_key : str
            The key of the job to retrieve.

        Raises
        ------
        JobKeyDoesNotExist
            If no job associated with the given job key exists yet.
        """
        try:
            job_config_file = cls._cache_dir(job_key) / "job.json"
            with open(job_config_file, "r") as f:
                return _JobModel.model_validate_json(f.read()).as_job()
        except FileNotFoundError as e:
            logger.error(e)
            raise JobDoesNotExistError(job_key)
        except ValueError as e:
            logger.error(e)
            raise

    def execute(self) -> None:
        """Execute the runs comprising the job."""
        self._verify_output_dir_empty()
        self._init_cache()
        self._write_job_config()
        for run in self._runs:
            run.execute()

    def _write_job_config(self) -> None:
        with open(self._cache_dir(self.key) / "job.json", "w") as f:
            f.write(_JobModel.from_job(self).model_dump_json(by_alias=True))

    @staticmethod
    def _cache_dir(key: str) -> Path:
        return get_cache_dir() / "jobs" / key

    def _init_cache(self) -> None:
        self._cache_dir(self.key).mkdir(exist_ok=True, parents=True)

    def delete(self, interactive=True) -> None:
        """Delete all results data for the job.

        Users should be careful to ensure that the ``results_dir`` specified in
        the constructor is indeed the targeted run directory. This is a
        destructive operation and should be used with care. E.g. if
        ``results_dir = Path('/')`` this would cause the deletion of all files
        on the system that the user has write permissions for.

        Parameters
        ----------
        interactive : bool, optional
            Whether or not the ``delete`` command should be run interactively.
            When ``True`` (the default), the user will be prompted to confirm
            the deletion of the job results data. When ``False``, no
            confirmation prompt will be given. The latter option is provided to
            support programmatic usage, e.g. to delete the data for all jobs in
            a collection of jobs.
        """

        def confirm(key: str) -> bool:
            answer = input(f"Delete job '{key}'? [y/N]")
            if answer.lower() in ["y", "yes"]:
                return True
            else:
                return False

        def proceed():
            for run in self._runs:
                run.delete(interactive=False)
            if (
                len(
                    list(self._get_job_output_dir(self.results_dir, self.key).iterdir())
                )
                != 0
            ):
                raise RuntimeError(f"Could not delete all run data for job {self.key}")
            self._get_job_output_dir(self.results_dir, self.key).rmdir()

        if not interactive or confirm(self.key):
            proceed()

    def _verify_output_dir_empty(self) -> None:
        """Ensure that ``self.results_dir/self.key`` does not contain any
        regular files.

        If ``self.results_dir/self.key`` does contain regular files, this is
        interpreted as meaning that a job of the given name already exists.

        Raises
        ------
        JobExistsError
            If the specified output_dir already contains regular files.
        """
        output_dir = self._get_job_output_dir(self.results_dir, self.key)
        if output_dir.is_dir():
            # output_dir exists
            if any(output_dir.iterdir()):
                # output_dir contains files
                raise JobExistsError(self.results_dir, self.key)

    @property
    def run_meta(self) -> pd.DataFrame:
        """Return metadata about each run in the job.

        Returns
        -------
        pd.DataFrame
            A DataFrame with columns:
                * ``run_id``: The index of the run in the job.
                * ``program``: The path to the FRED entrypoint file.
                * ``synth_pop``: The name of the synthetic population used.
                * ``locations``: The locations in the synthetic population.
                * ``start_date``: The start date of the simulation.
                * ``end_date``: The end date of the simulation.
                * ``params``: The model parameters.
                * ``seed``: The random seed used for the run.
                * ``size``: The instance size used for the run.
        """

        def proc_date(date: Optional[date]) -> Union[pd.Timestamp, NaTType]:
            return pd.Timestamp(date) if date is not None else pd.NaT

        return pd.DataFrame(
            {
                "run_id": run_id,
                "program": str(run.params.program),
                "synth_pop": run.params.synth_pop.name,
                "locations": run.params.synth_pop.locations,
                "start_date": proc_date(run.params.start_date),
                "end_date": proc_date(run.params.end_date),
                "params": run.params.model_params,
                "seed": run.params.seed,
                "size": run.size,
            }
            for run_id, run in enumerate(self._runs)
        )

    @property
    def status(self) -> JobStatus:
        """Current status of the job."""
        return JobStatus((run_id, run.status) for run_id, run in enumerate(self._runs))

    @property
    def results(self) -> JobResults:
        """Object providing access to simulation results."""
        completed_run_results_with_ids = (
            (run_id, run.results)
            for run_id, run in enumerate(self._runs)
            if run.status.name == "DONE" and run.results is not None
        )
        return JobResults(completed_run_results_with_ids)

    def __repr__(self) -> str:
        return (
            f"Job("
            f"program={self.program}, "
            f"config={self.config}, "
            f"key={self.key}, "
            f"size={self.size}, "
            f"fred_version={self.fred_version}, "
            f"results_dir={self.results_dir}"
            f")"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Job):
            return False
        return (
            self.program == other.program
            and self.config == other.config
            and self.key == other.key
            and self.size == other.size
            and self.fred_version == other.fred_version
            and self.results_dir == other.results_dir
        )


class JobExistsError(Exception):
    """Raised when a job with a requested key already exists in the results."""

    def __init__(self, results_dir: Path, key: str):
        self.results_dir = results_dir
        self.key = key
        super().__init__(
            f"A job with key '{key}' already exists in results directory "
            f"'{results_dir}'"
        )


class JobDoesNotExistError(Exception):
    """Raised when a job with a requested key does not exist in the cache."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"No job with key '{key}' exists")
