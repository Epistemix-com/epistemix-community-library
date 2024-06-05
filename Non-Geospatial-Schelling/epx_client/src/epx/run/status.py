from abc import ABC, abstractmethod
from datetime import datetime
import itertools
from pathlib import Path
import re
from typing import Any, Iterable, Literal, NamedTuple, TypeGuard, Union, get_args

import pandas as pd

from epx.run.fs import FileFinderF11, FileFinderF10, FileFinder

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
StatusName = Literal["NOT STARTED", "RUNNING", "ERROR", "DONE"]


class LogItem(NamedTuple):
    """An individual entry in the logs generated by FRED.

    Attributes
    ----------
    level : LogLevel
        The log level of the message, e.g. `INFO`, `ERROR`, etc.
    time : datetime
        The time that the message was reported at.
    message : str
        The log message.
    """

    level: LogLevel
    time: datetime
    message: str


class RunStatus(ABC):
    """Base class for returning run status information."""

    def __init__(self, file_finder: FileFinder):
        self._base_file_finder = file_finder

    @property
    @abstractmethod
    def logs(self) -> pd.DataFrame:
        """Return a collection of log entries output by FRED.

        Returns
        -------
        pd.DataFrame
            Collection of individual log entries generated by FRED during the
            run.
        """
        ...

    @property
    def name(self) -> StatusName:
        """Return a string summarizing the run status.

        Returns
        -------
        Status
            A string indicating the status of the job, one of: `"NOT STARTED"`,
            `"RUNNING"`, `"ERROR"`, or `"DONE"`.
        """
        try:
            with open(self._base_file_finder.return_code, "r") as f:
                try:
                    return_code = int(f.read().strip())
                except ValueError:
                    # return code file has been created, but not yet written to.
                    return "RUNNING"
                if return_code == 0:
                    return "DONE"
                else:
                    return "ERROR"
        except FileNotFoundError:
            if not self._base_file_finder.run_output_dir.exists():
                return "NOT STARTED"
            return "RUNNING"

    def __str__(self):
        return self.name

    @staticmethod
    def _is_valid_log_level(level: str) -> TypeGuard[LogLevel]:
        """Helper method for validating that a string is a valid log level."""
        return level in get_args(LogLevel)


class RunStatusF10(RunStatus):
    """Accessor for information about the status of a run.

    Notes
    -----
    This implementation is for runs of FRED <= 10.1.0.
    """

    def __init__(self, file_finder: FileFinderF10):
        """LegacyRunStatus constructor.

        Parameters
        ----------
        file_finder : LegacyFileFinder
            Accessor for filesystem paths of FRED output files for FRED
            <=10.1.0.
        """
        super().__init__(file_finder)
        self._file_finder = file_finder

    @property
    def logs(self) -> pd.DataFrame:
        try:
            log_iterators = [self._parse_status_file(self._file_finder.status)]
        except FileNotFoundError:
            log_iterators = []
        if self._file_finder.errors is not None:
            log_iterators.append(self._parse_errors_file(self._file_finder.errors))
        return pd.DataFrame.from_records(
            tuple(itertools.chain(*log_iterators)), columns=["level", "time", "message"]
        )

    @staticmethod
    def _parse_status_file(p: Path) -> Iterable[LogItem]:
        """Helper method to parse status.txt"""
        file_write_time = datetime.fromtimestamp(p.stat().st_mtime)
        with open(p, "r") as f:
            for line in f.readlines():
                trimmed_line = line.strip()
                if trimmed_line:
                    yield LogItem("INFO", file_write_time, trimmed_line)

    @staticmethod
    def _parse_errors_file(p: Path) -> Iterable[LogItem]:
        """Helper method to parse errors.txt."""
        file_write_time = datetime.fromtimestamp(p.stat().st_mtime)
        with open(p, "r") as f:
            messages = [x.strip() for x in f.read().split("FRED ERROR: ") if x]
        return tuple(LogItem("ERROR", file_write_time, m) for m in messages)

    def __repr__(self):
        return f"RunStatusF10({self._file_finder})"


class RunStatusF11(RunStatus):
    """Accessor for information about the status of a run.

    Notes
    -----
    This implementation is for runs of FRED >= 11.0.0.
    """

    def __init__(self, file_finder: FileFinderF11):
        super().__init__(file_finder)
        self._file_finder = file_finder
        self._log_re = re.compile(
            r"^\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z)\] ([A-Z]*): (.*)$"
        )

    @property
    def logs(self) -> pd.DataFrame:
        def process_log_line(line: str) -> LogItem:
            m = self._log_re.match(line)
            if m is None:
                raise ValueError(f"Invalid logline: {line}")
            level = m.group(2)
            assert self._is_valid_log_level(level)
            return LogItem(
                level,
                datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S.%fZ"),
                m.group(3),
            )

        try:
            with open(self._file_finder.logs, "r") as f:
                log_records = tuple(process_log_line(line) for line in f.readlines())
        except FileNotFoundError:
            log_records = tuple()
        return pd.DataFrame.from_records(
            log_records, columns=["level", "time", "message"]
        )

    def __repr__(self):
        return f"RunStatusF11({self._file_finder})"


class RunStatusFactory:
    """Factory for selecting correct RunStatus implementation."""

    def __init__(self, file_finder: Union[FileFinderF10, FileFinderF11]):
        self.file_finder = file_finder

    def build(self) -> RunStatus:
        """Obtain a RunStatus appropriate for the given output directory.

        Raises
        ------
        TypeError
            If given `file_finder` is not a recognized type.
        """
        if self._is_legacy_file_finder(self.file_finder):
            return RunStatusF10(self.file_finder)
        elif self._is_file_finder(self.file_finder):
            return RunStatusF11(self.file_finder)
        else:
            raise TypeError(f"{self.file_finder} is not a valid FileFinder type")

    @staticmethod
    def _is_legacy_file_finder(file_finder: Any) -> TypeGuard[FileFinderF10]:
        if isinstance(file_finder, FileFinderF10):
            return True
        return False

    @staticmethod
    def _is_file_finder(file_finder: Any) -> TypeGuard[FileFinderF11]:
        if isinstance(file_finder, FileFinderF11):
            return True
        return False
