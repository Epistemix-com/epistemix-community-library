from abc import ABC, abstractmethod
from pathlib import Path
import re
from typing import Iterable, Literal, NamedTuple, Optional, Union

CountType = Literal["count", "new", "cumulative"]


class OutputDirectoryError(Exception):
    def __init__(self, output_dir: Path, fred_version: Optional[str] = None):
        if fred_version is not None:
            message = (
                f"{output_dir} is not a valid FRED {fred_version} output directory."
            )
        else:
            message = f"{output_dir} is not a valid FRED output directory."
        super().__init__(message)


class VarBySimDayPath(NamedTuple):
    """Metadata about a file with the value of a variable on a sim day."""

    sim_day: int
    path: Path


class FileFinder(ABC):
    def __init__(self, run_output_dir: Path):
        """Base class for file finders used to find output across
        multiple versions of FRED.

        Abstracts filesystem locations to required files.

        Parameters
        ----------
        run_output_dir : Path
            The root directory for all files generated for a particular
            run. This directory should contain e.g. `conditions.json`,
            _NOT_ e.g. a directory called `RUN1`.
        """
        self.run_output_dir = run_output_dir

    @staticmethod
    def _validate_file_exists(p: Path) -> None:
        if not p.is_file():
            raise FileNotFoundError(f"File '{p}' not found.")

    def state(self, condition: str, state: str, count_type: CountType) -> Path:
        def get_prefix(count_type: CountType) -> str:
            match count_type:
                case "count":
                    return ""
                case "new":
                    return "new"
                case "cumulative":
                    return "tot"
                case _:
                    raise ValueError(f"State count type '{count_type}' invalid.")

        p = (
            self.run_output_dir
            / f"DAILY/{condition}.{get_prefix(count_type)}{state}.txt"
        )
        self._validate_file_exists(p)
        return p

    @property
    def dates(self) -> Path:
        p = self.run_output_dir / "DAILY/Date.txt"
        self._validate_file_exists(p)
        return p

    @property
    def epi_week(self) -> Path:
        p = self.run_output_dir / "DAILY/EpiWeek.txt"
        self._validate_file_exists(p)
        return p

    @property
    def pop_size(self) -> Path:
        p = self.run_output_dir / "DAILY/Popsize.txt"
        self._validate_file_exists(p)
        return p

    @property
    def conditions(self) -> Path:
        p = self.run_output_dir / "conditions.json"
        self._validate_file_exists(p)
        return p

    @property
    def return_code(self) -> Path:
        p = self.run_output_dir / "return_code.txt"
        self._validate_file_exists(p)
        return p

    @property
    @abstractmethod
    def print_output(self) -> Path: ...

    @abstractmethod
    def csv_output(self, filename: str) -> Path: ...

    @abstractmethod
    def text_output(self, filename: str) -> Path: ...

    @abstractmethod
    def numeric(self, varname: str) -> Path: ...

    @abstractmethod
    def list_table_by_simday(self, varname: str) -> Iterable[VarBySimDayPath]: ...

    @abstractmethod
    def table_by_simday(self, varname: str) -> Iterable[VarBySimDayPath]: ...

    @abstractmethod
    def network(self, network_name: str, sim_day: int) -> Path: ...


class FileFinderF10(FileFinder):
    """Accessor for filesystem paths of FRED output files for FRED <=10.1.0."""

    def __init__(self, output_dir: Path, run_number: Optional[int] = None):
        """Constructor for FileFinderF10.

        Parameters
        ----------
        output_dir : Path
            Path to simulation output directory corresponding to FRED's
            `--directory` argument.
        run_number : int, optional
            The run number to use for the simulation output directory. This
            argument is only required if the output directory does not yet
            exist, and is used to identify the expected run directory within
            the simulation output directory. By default `None`.

        Raises
        ------
        FileNotFoundError
            If a unique run directory could not be identified in the simulation
            output directory.
        """
        self.output_dir = output_dir
        super().__init__(self._get_run_output_dir(output_dir, run_number))

    @staticmethod
    def _get_run_output_dir(output_dir: Path, run_number: Optional[int] = None) -> Path:
        """Helper method to identify run directory within the simulation output
        directory.

        Notes
        -----
        In FRED <= 10.1.0, the simulation output directory contained
        (potentially) multiple runs. The name of each run directory was
        determined from FRED's ``--run-number`` argument, e.g. ``RUN1``,
        ``RUN12``, etc. This implementation requires that the simulation
        output directory contains only a single run.

        If the ``run_number`` argument is provided, the run directory is
        returned as ``<run_number>/RUN<run_number>``. Otherwise, we check
        for a single directory in the simulation output directory following
        the correct naming convention, and identify that as the run directory.

        Raises
        ------
        FileNotFoundError
            If a unique run directory could not be identified in the simulation
            output directory.
        """
        if run_number is not None:
            return output_dir / f"RUN{run_number}"
        candidate_run_dirs = [x for x in output_dir.glob("RUN*")]
        if len(candidate_run_dirs) != 1:
            raise FileNotFoundError(
                f"Could not identify unique run directory in {output_dir}"
            )
        return candidate_run_dirs[0]

    @property
    def print_output(self) -> Path:
        p = self.run_output_dir / "fred_out.txt"
        self._validate_file_exists(p)
        return p

    def csv_output(self, filename: str) -> Path:
        p = self.run_output_dir / f"CSV/{filename}"
        self._validate_file_exists(p)
        return p

    def text_output(self, filename: str) -> Path:
        p = self.run_output_dir / f"CSV/{filename}"
        self._validate_file_exists(p)
        return p

    def numeric(self, varname: str) -> Path:
        p = self.run_output_dir / f"DAILY/FRED.{varname}.txt"
        self._validate_file_exists(p)
        return p

    def list_table_end_of_sim(self, varname: str) -> Path:
        p = self.run_output_dir / f"LIST/{varname}.txt"
        self._validate_file_exists(p)
        return p

    def list_table_by_simday(self, varname: str) -> Iterable[VarBySimDayPath]:
        all_paths = self._var_by_simday_paths(varname)
        if len(all_paths) == 0:
            raise FileNotFoundError(
                f"No outputs for list table variable {varname} by sim day found."
            )
        return (x for x in all_paths)

    def table_end_of_sim(self, varname: str) -> Path:
        p = self.run_output_dir / f"LIST/{varname}.txt"
        self._validate_file_exists(p)
        return p

    def table_by_simday(self, varname: str) -> Iterable[VarBySimDayPath]:
        all_paths = self._var_by_simday_paths(varname)
        if len(all_paths) == 0:
            raise FileNotFoundError(
                f"No outputs for table variable {varname} by sim day found."
            )
        return (x for x in all_paths)

    def list_end_of_sim(self, varname: str) -> Path:
        p = self.run_output_dir / f"LIST/{varname}.txt"
        self._validate_file_exists(p)
        return p

    def list_by_simday(self, varname: str) -> Iterable[VarBySimDayPath]:
        all_paths = self._var_by_simday_paths(varname)
        if len(all_paths) == 0:
            raise FileNotFoundError(
                f"No outputs for list variable {varname} by sim day found."
            )
        return (x for x in all_paths)

    def network(self, network_name: str, sim_day: int) -> Path:
        p = self.run_output_dir / f"{network_name}-{sim_day}.vna"
        self._validate_file_exists(p)
        return p

    def _var_by_simday_paths(self, varname: str) -> list[VarBySimDayPath]:
        def get_sim_day(p: Path) -> int:
            m = re.match(r"\w*-(\d*).txt", p.name)
            if m is None:
                raise ValueError(f"{p} not recognized variable by sim day file")
            return int(m.group(1))

        all_paths = [
            VarBySimDayPath(get_sim_day(x), x)
            for x in (self.run_output_dir / "LIST").glob(f"{varname}-*.txt")
        ]
        all_paths.sort(key=lambda x: x.sim_day)
        return all_paths

    @property
    def errors(self) -> Optional[Path]:
        """Path to file containing details of any errors.

        Returns
        -------
        Path, optional
            Path to the errors file for the run, if one exists. Otherwise
            `None`.
        """
        p = self.run_output_dir / "errors.txt"
        try:
            self._validate_file_exists(p)
            return p
        except FileNotFoundError:
            return None

    @property
    def status(self) -> Path:
        p = self.run_output_dir / "status.txt"
        self._validate_file_exists(p)
        return p

    def __repr__(self) -> str:
        return f"FileFinderF10('{self.output_dir}')"


class FileFinderF11(FileFinder):
    """Accessor for filesystem paths of FRED output files for FRED >=11.0.0."""

    def __init__(self, output_dir: Path):
        """Constructor for FileFinderF11.

        Parameters
        ----------
        output_dir : Path
            Path to simulation output directory corresponding to FRED's
            `--directory` argument.
        """
        self.output_dir = output_dir
        super().__init__(output_dir)

    @property
    def print_output(self) -> Path:
        p = self.run_output_dir / "USER_OUTPUT/print_output.txt"
        self._validate_file_exists(p)
        return p

    def csv_output(self, filename: str) -> Path:
        p = self.run_output_dir / f"USER_OUTPUT/{filename}"
        self._validate_file_exists(p)
        return p

    def text_output(self, filename: str) -> Path:
        p = self.run_output_dir / f"USER_OUTPUT/{filename}"
        self._validate_file_exists(p)
        return p

    def numeric(self, varname: str) -> Path:
        p = self.run_output_dir / f"VARIABLES/numeric.{varname}.csv"
        self._validate_file_exists(p)
        return p

    def list_table_by_simday(self, varname: str) -> Iterable[VarBySimDayPath]:
        all_paths = self._var_by_simday_paths(varname, "list_table")
        if len(all_paths) == 0:
            raise FileNotFoundError(
                f"No outputs for list table variable {varname} by sim day found."
            )
        return (x for x in all_paths)

    def table_by_simday(self, varname: str) -> Iterable[VarBySimDayPath]:
        all_paths = self._var_by_simday_paths(varname, "table")
        if len(all_paths) == 0:
            raise FileNotFoundError(
                f"No outputs for table variable {varname} by sim day found."
            )
        return (x for x in all_paths)

    def list_(self, varname: str) -> Path:
        p = self.run_output_dir / f"VARIABLES/list.{varname}.csv"
        self._validate_file_exists(p)
        return p

    def network(self, network_name: str, sim_day: int) -> Path:
        p = self.run_output_dir / f"NETWORKS/{network_name}-{sim_day}.gv"
        self._validate_file_exists(p)
        return p

    def _var_by_simday_paths(self, varname: str, prefix: str) -> list[VarBySimDayPath]:
        def get_sim_day(p: Path) -> int:
            m = re.match(r"^[\w\.]*-(\d*)\.csv", p.name)
            if m is None:
                raise ValueError(f"{p} not recognized variable by sim day file")
            return int(m.group(1))

        all_paths = [
            VarBySimDayPath(get_sim_day(x), x)
            for x in (self.run_output_dir / "VARIABLES").glob(
                f"{prefix}.{varname}-*.csv"
            )
        ]
        all_paths.sort(key=lambda x: x.sim_day)
        return all_paths

    @property
    def logs(self) -> Path:
        """Path to log file.

        Returns
        -------
        Path
            Path to the log file for the run.
        """
        p = self.run_output_dir / "logs.txt"
        self._validate_file_exists(p)
        return p

    def __repr__(self) -> str:
        return f"FileFinderF11('{self.output_dir}')"


class FileFinderFactory:
    """Factory for selecting correct FileFinder implementation.

    Returns the appropriate FileFinder by inspecting the given output directory
    structure.

    Notes
    -----
        If the FRED `output_dir` provided to this class's constructor contains
        directories named like 'RUN*' then it is deemed to be a legacy
        results directory (FRED <= 10.1.0). Otherwise it is identified as a
        standard run results directory.

        run_number can be used to specify the expected location of a set of
        FRED<=10 results in case FRED has not already created the output
        directory at the time the FileFinder is instantiated.
    """

    def __init__(self, output_dir: Path, run_number: Optional[int] = None):
        self.output_dir = output_dir
        self.run_number = run_number

    def build(self) -> Union[FileFinderF10, FileFinderF11]:
        """Obtain a FileFinder appropriate for the given output directory.

        Notes
        -----
        We perform the following checks to determine the appropriate FileFinder:
        * If ``run_number`` was specified in the constructor, the output
          directory is assumed to be a legacy FRED output directory and a
          FileFinderF10 is returned.
        * If the output directory matches the structure of a FRED >= 11 results
          directory, a FileFinderF11 instance is returned.
        * If the output directory matches the structure of a FRED < 11 results
          directory, a FileFinderF10 instance is returned.
        * Otherwise, we assume the output directory is a yet-to-be-populated
          FRED >= 11 results directory.
        """
        if self.run_number is not None:
            return FileFinderF10(self.output_dir, self.run_number)
        elif self._is_output_dir(self.output_dir):
            return FileFinderF11(self.output_dir)
        elif self._is_legacy_output_dir(self.output_dir):
            return FileFinderF10(self.output_dir)
        else:
            return FileFinderF11(self.output_dir)

    @staticmethod
    def _is_legacy_output_dir(output_dir: Path) -> bool:
        candidate_run_dirs = [x for x in output_dir.glob("RUN*")]
        if len(candidate_run_dirs) != 0:
            return True
        return False

    @staticmethod
    def _is_output_dir(output_dir: Path) -> bool:
        try:
            if "conditions.json" in [x.name for x in output_dir.iterdir()]:
                return True
        except FileNotFoundError:
            return False
        return False
