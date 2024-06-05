from abc import ABC, abstractmethod
import functools
from pathlib import Path
import re
from typing import Any, Callable, Iterable, Optional, Union, TypeGuard

import pandas as pd
import networkx as nx

from epx.run.fs import (
    CountType,
    FileFinderF11,
    FileFinderF10,
    FileFinder,
    VarBySimDayPath,
)


class RunResults(ABC):
    def __init__(self, file_finder: FileFinder):
        self._base_file_finder = file_finder

    def state(self, condition: str, state: str, count_type: CountType) -> pd.DataFrame:
        """Return a time series of agent occupancy of a given FRED state.

        Parameters
        ----------
        condition : str
            Name of the FRED model condition containing the target state.
        state : str
            Name of the target state.
        count_type : CountType
            Type of count to report. Options are:
                * `count`, the number of agents occupying the state at the end
                  of each simulated day.
                * `new`, the number of agents entering the state at any time
                  during each simulated day.
                * `cumulative`, the cumulative number of times any agent has
                  entered the state since the beginning of the simulation,
                  reported at the end of each simulated day.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * `sim_day`
                * The name of the requested count type, i.e. one of `count`,
                  `new`, or `cumulative`.
        """
        return pd.read_csv(
            self._base_file_finder.state(condition, state, count_type),
            header=None,
            sep=" ",
            names=["sim_day", count_type],
        )

    def pop_size(self) -> pd.DataFrame:
        """Return a time series of population size during the run.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * `sim_day`
                * `pop_size`.
        """
        return pd.read_csv(
            self._base_file_finder.pop_size,
            header=None,
            sep=" ",
            names=["sim_day", "pop_size"],
        )

    def epi_weeks(self) -> pd.DataFrame:
        """Return a mapping from simulation days to epidemiological weeks.

        An epidemiological week, commonly referred to as an epi week or a CDC
        week, is a standardized method of counting weeks to allow for the
        comparison of data year after year.

        By definition, the first epi week of the year ends on the first Saturday
        of January that falls at least four days into the month. Each epi week
        begins on a Sunday and ends on a Saturday.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * `sim_day`
                * `epi_week` with string values in `YYYY.MM` format.
        """
        return pd.read_csv(
            self._base_file_finder.epi_week,
            header=None,
            sep=" ",
            names=["sim_day", "epi_week"],
            dtype={"sim_day": int, "epi_week": str},
        )

    def dates(self) -> pd.DataFrame:
        """Return a mapping from simulation days to calendar dates.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * `sim_day`
                * `sim_date`
        """
        return pd.read_csv(
            self._base_file_finder.dates,
            header=None,
            sep=" ",
            names=["sim_day", "sim_date"],
            parse_dates=["sim_date"],
        )

    def print_output(self) -> pd.Series:
        """Return a series of messages output by FRED's `print()` action.

        Returns
        -------
        pd.Series
            A series of `print()` output messages.
        """
        with open(self._base_file_finder.print_output, "r") as f:
            return pd.Series([x.strip() for x in f.readlines()]).rename("print_output")

    def csv_output(self, filename: str) -> pd.DataFrame:
        """Return data output by FRED's `print_csv` action.

        Parameters
        ----------
        filename : str
            Name of output file as specified in the calls to `print_csv` in
            the FRED model code.

        Returns
        -------
        pd.DataFrame
            DataFrame containing data written to `filename`. Columns are those
            specified in the call to `open_csv` in the model code.
        """
        return pd.read_csv(self._base_file_finder.csv_output(filename))

    def file_output(self, filename: str) -> pd.Series:
        """Return data output by FRED's `print_file` action.

        Parameters
        ----------
        filename : str
            Name of output file as specified in the calls to `print_file` in
            the FRED model code.

        Returns
        -------
        pd.Series
            Series containing data written to `filename`. Each entry is a string
            containing the complete output for each call to `print_file` within
            the model code.
        """
        with open(self._base_file_finder.text_output(filename), "r") as f:
            return pd.Series([x.strip() for x in f.readlines()]).rename("file_output")

    def numeric_var(self, varname: str) -> pd.DataFrame:
        """Return a time series of the value of a shared numeric variable.

        Parameters
        ----------
        varname : str
            Name of the shared numeric variable.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * `sim_day`
                * `value`
        """
        return pd.read_csv(
            self._base_file_finder.numeric(varname),
            header=None,
            sep=" ",
            names=["sim_day", "value"],
        )

    @abstractmethod
    def list_var(self, varname: str, wide: bool) -> pd.DataFrame:
        """Return a time series of the value of a shared list variable.

        Parameters
        ----------
        varname : str
            Name of the shared list variable.
        wide : bool, optional
            Return data in 'wide' format where a column is created for each
            list element. Defaults to ``False``.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * `sim_day`
                * `list_index`
                * `value`
            if ``wide=False``. Otherwise:
                * `sim_day`
                * `item_0`
                * `item_1`
                * ...
        """
        ...

    @abstractmethod
    def list_table_var(self, varname: str, wide: bool) -> pd.DataFrame:
        """Return a time series of the value of a shared list_table variable.

        Parameters
        ----------
        varname : str
            Name of the shared list_table variable.
        wide : bool, optional
            Return data in 'wide' format where a column is created for each
            list element. Defaults to ``False``.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * `sim_day`
                * `key`
                * `list_index`
                * `value`
            if ``wide=False``. Otherwise:
                * `sim_day`
                * `key`
                * `item_0`
                * `item_1`
                * ...
        """
        ...

    @abstractmethod
    def table_var(self, varname: str) -> pd.DataFrame:
        """Return a time series of the value of a shared table variable.

        Parameters
        ----------
        varname : str
            Name of the shared table variable.

        Returns
        -------
        pd.DataFrame
                * `sim_day`
                * `key`
                * `value`
        """
        ...

    @abstractmethod
    def network(
        self, network_name: str, is_directed: bool = True, sim_day: Optional[int] = None
    ) -> nx.Graph:
        """Reads a single day's network from the output files. Returns a networkx graph.

        Parameters
        ----------
        network_name : str
            Name of the network.
        is_directed : bool, optional
            Whether the network is directed or not. Defaults to ``True``.
        sim_day : int, optional
            The simulation day to read the network for. If not provided, the
            network for the last day of the simulation is read.

        Returns
        -------
        nx.Graph
        """
        ...

    @staticmethod
    def _str_to_numeric(s: str) -> Union[int, float]:
        def is_int(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        if is_int(s):
            return int(s)
        return float(s)

    @staticmethod
    def _read_table_file(filepath: Path) -> pd.DataFrame:
        """Read files with two columns where col1 is key and col2 is value."""
        return pd.read_csv(filepath, names=["key", "value"], skiprows=[0])

    @classmethod
    def _read_wide_list_file(cls, filepath: Path, value_pattern: str) -> pd.DataFrame:
        """Reads a file in a wide list format.

        These are files with structure:

            <variable>,value
            0,<list_string_repr>
            1,<list_string_repr>

        Where:
            * `<variable>` specifies what each row represents (e.g. `day` or
              `key`)
            * `<list_string_repr>` is a string representation of a list, e.g.
              `"[0.000000,0.000000,0.000000]"`, `13.200000,26.400000`, or
              `13.200000` where the last example is interpreted as a list of
              length 1.

        Parameters
        ----------
        filepath : Path
            Path to the file to read
        value_pattern : str
            A regular expression with a single capturing group that extracts a
            string of comma separated numbers from the <list_string_repr> (as
            defined above) appropriate for the given file. The idea is that
            hitting the extracted capturing group with `str.split(",")` will
            yield a list of strings representing numbers.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: `<variable>`, `list_index`, `value`.
        """

        def parse_line(line: str, value_pattern: str) -> tuple[Union[int, float], str]:
            m = re.match(r"([\d\.]*)," + value_pattern, line)
            if m is None:
                raise ValueError(f"Unrecognized wide list line: {line}")
            return cls._str_to_numeric(m.group(1)), m.group(2)

        def add_list_index_col(df):
            return (
                df.assign(tmp=1)
                .assign(list_index=lambda df: df["tmp"].cumsum() - 1)
                .drop(columns="tmp")
            )

        with open(filepath, "r") as f:
            col_names = [x.strip().lower() for x in f.readline().split(",")]
            col_names[1] = "value"
            lines = f.readlines()
            if not lines:
                data = None
            else:
                data = (parse_line(line, value_pattern) for line in lines)

        if data is None:
            return pd.DataFrame(columns=[col_names[0], "list_index", col_names[1]])
        else:
            return (
                pd.DataFrame.from_records(data, columns=col_names)
                .pipe(
                    lambda df: (
                        df.loc[:, [col_names[0]]].join(
                            df.loc[:, col_names[1]]
                            .str.split(",")
                            .explode()
                            .rename(col_names[1])
                            .astype(float)
                        )
                    )
                )
                .pipe(
                    lambda df: df.groupby(col_names[0])[col_names].apply(
                        add_list_index_col
                    )
                )
                .loc[:, [col_names[0], "list_index", col_names[1]]]
                .reset_index(drop=True)
            )

    @staticmethod
    def _add_wide_option(func):
        """Decorate a method to report list variables in 'wide' format.

        Long format data for a list variable, for example, looks like:

        .. code-block:: text

                sim_day  list_index  value
            0         0           0    0.0
            1         0           1    0.0
            2         0           2    0.0
            3         1           0    1.1
            4         1           1    2.2
            5         1           2    3.3

        This decorator looks for ``wraps=True`` among the keyword arguments
        passed to the decorated method and, if found, pivots the data into
        the form:

        .. code-block:: text

                sim_day  item_0  item_1  item_2
            0         0     0.0     0.0     0.0
            1         1     1.1     2.2     3.3

        Parameters
        ----------
        func : Callable[[RunResults, str], pd.DataFrame]
            Function that reads either a list or list_table variable in long
            format.

        Returns
        -------
        Callable[[RunResults, str], pd.DataFrame]
            Decorated method that implements pivot from long to wide data shape.
        """

        @functools.wraps(func)
        def inner(*args, **kwargs):
            if "wide" in kwargs.keys():
                wide = kwargs.pop("wide")
                if wide:
                    df = func(*args, **kwargs)
                    ix_cols = [x for x in df.columns if x != "value"]
                    return (
                        df.set_index(ix_cols)["value"]
                        .unstack()
                        .rename_axis(columns=None)
                        .rename(columns=lambda x: f"item_{x}")
                        .reset_index()
                    )
            return func(*args, **kwargs)

        return inner


class RunResultsF10(RunResults):
    def __init__(self, file_finder: FileFinderF10):
        super().__init__(file_finder)
        self._file_finder = file_finder

    @RunResults._add_wide_option
    def list_var(self, varname: str, wide: bool = False) -> pd.DataFrame:
        return self._read_complex_variable_time_series(
            varname,
            ["sim_day", "list_index", "value"],
            self._read_list_file,
            self._file_finder.list_by_simday,
            self._file_finder.list_end_of_sim,
        )

    @RunResults._add_wide_option
    def list_table_var(self, varname: str, wide: bool = False) -> pd.DataFrame:
        return self._read_complex_variable_time_series(
            varname,
            ["sim_day", "key", "list_index", "value"],
            functools.partial(self._read_wide_list_file, value_pattern=r"([\d,\.]*)"),
            self._file_finder.list_table_by_simday,
            self._file_finder.list_table_end_of_sim,
        )

    def table_var(self, varname: str) -> pd.DataFrame:
        return self._read_complex_variable_time_series(
            varname,
            ["sim_day", "key", "value"],
            self._read_table_file,
            self._file_finder.table_by_simday,
            self._file_finder.table_end_of_sim,
        )

    def network(
        self, network_name: str, is_directed: bool = True, sim_day: Optional[int] = None
    ) -> nx.Graph:
        if sim_day is None:
            sim_day = self.dates().iloc[-1]["sim_day"] + 1
        filepath = self._file_finder.network(network_name, sim_day)

        # create a Graph or DiGraph object
        G: Union[nx.DiGraph, nx.Graph]
        if is_directed:
            G = nx.DiGraph(name=network_name)
        else:
            G = nx.Graph(name=network_name)

        # read in data from file
        with open(filepath, "r") as f:
            lines = f.readlines()

        tie_data_index = lines.index("*tie data\n")
        node_data = lines[:tie_data_index]
        tie_data = lines[tie_data_index:]

        # construct a list of nodes
        node_count = 0
        nodes = []
        node_attr_keys = node_data[1].strip().split(" ")[1:]
        for line in node_data[2:]:
            line_list = line.strip().split(" ")
            node_id = line_list[0]
            node_attrs = line_list[1:]
            nodes.append((node_id, dict(zip(node_attr_keys, node_attrs))))
            node_count += 1

        # construct a list of ties
        tie_count = 0
        ties = []
        tie_attr_keys = tie_data[1].strip().split(" ")[2:]
        for line in tie_data[2:]:
            line_list = line.strip().split(" ")
            from_id = line_list[0]
            to_id = line_list[1]
            tie_attrs = line_list[2:]
            ties.append((from_id, to_id, dict(zip(tie_attr_keys, tie_attrs))))
            tie_count += 1

        G.add_nodes_from(nodes)
        G.add_edges_from(ties)

        return G

    def _read_complex_variable_time_series(
        self,
        varname: str,
        col_names: list[str],
        read_file: Callable[[Path], pd.DataFrame],
        interval_output_files: Callable[[str], Iterable[VarBySimDayPath]],
        end_of_sim_output_file: Callable[[str], Path],
    ) -> pd.DataFrame:
        """Read list, table, or list table as a time series.

        FRED 10 outputs two types of file for variables with complex data types:

        * {varname}-{sim_day}.txt if the variable is output with a specified
          interval
        * {varname}.txt at the end of the simulation (if this is turned on)

        This method uses the `read_file` callable to read all available
        individual files into data frames with `col_names`, and returns the data
        as a single data frame.

        Here we also handle the logic for:

        1. Using only end of simulation outputs, because interval outputs
           weren't turned on.
        2. Using only daily interval outputs, because end of simulation outputs
           weren't turned on
        3. Combining daily interval and end of simulation outputs in case both
           were turned on, and the last daily interval output occurred before
           the end of the simulation.
        """

        def outputs_by_simday(
            varname: str,
            col_names: list[str],
            read_file: Callable[[Path], pd.DataFrame],
            interval_output_files: Callable[[str], Iterable[VarBySimDayPath]],
        ) -> Optional[pd.DataFrame]:
            try:
                return (
                    pd.concat(
                        [
                            read_file(x.path).assign(sim_day=x.sim_day)
                            for x in interval_output_files(varname)
                        ]
                    )
                    .reset_index(drop=True)
                    .loc[:, col_names]
                )
            except FileNotFoundError:
                return None

        def outputs_end_of_sim(
            varname: str,
            col_names: list[str],
            last_simday: pd.Timedelta,
            read_file: Callable[[Path], pd.DataFrame],
            end_of_sim_output_file: Callable[[str], Path],
        ) -> Optional[pd.DataFrame]:
            try:
                return (
                    read_file(end_of_sim_output_file(varname))
                    .assign(sim_day=last_simday)
                    .reset_index(drop=True)
                    .loc[:, col_names]
                )
            except FileNotFoundError:
                return None

        df = outputs_by_simday(varname, col_names, read_file, interval_output_files)
        last_simday = self.dates().iloc[-1]["sim_day"]

        if df is None:
            df_end_of_sim = outputs_end_of_sim(
                varname, col_names, last_simday, read_file, end_of_sim_output_file
            )
            if df_end_of_sim is None:
                raise FileNotFoundError(
                    f"Could not find results data for variable: {varname}"
                )
            else:
                return df_end_of_sim
        else:
            if df["sim_day"].max() < last_simday:
                df_end_of_sim = outputs_end_of_sim(
                    varname, col_names, last_simday, read_file, end_of_sim_output_file
                )
                if df_end_of_sim is None:
                    return df
                else:
                    return pd.concat([df, df_end_of_sim]).reset_index(drop=True)
            else:
                return df

    @staticmethod
    def _read_list_file(filepath: Path) -> pd.DataFrame:
        return (
            pd.read_csv(filepath, names=["value"], skiprows=[0])
            # Create list_index column
            .assign(tmp=1)
            .assign(list_index=lambda df: df["tmp"].cumsum() - 1)
            .drop(columns="tmp")
        )

    def __repr__(self):
        return f"RunResultsF10({self._file_finder})"


class RunResultsF11(RunResults):
    def __init__(self, file_finder: FileFinderF11):
        super().__init__(file_finder)
        self._file_finder = file_finder

    @RunResults._add_wide_option
    def list_var(self, varname: str, wide: bool = False) -> pd.DataFrame:
        return self._read_wide_list_file(
            self._file_finder.list_(varname), r'"\[([\d,\.]*)\]"'
        ).rename(columns={"day": "sim_day"})

    @RunResults._add_wide_option
    def list_table_var(self, varname: str, wide: bool = False) -> pd.DataFrame:
        return (
            pd.concat(
                [
                    (
                        self._read_wide_list_file(v.path, r'"\[([\d,\.]*)\]"')
                        .rename(columns={"day": "sim_day"})
                        .assign(sim_day=v.sim_day)
                    )
                    for v in self._file_finder.list_table_by_simday(varname)
                ]
            )
            .reset_index(drop=True)
            .loc[:, ["sim_day", "key", "list_index", "value"]]
        )

    def table_var(self, varname: str):
        return (
            pd.concat(
                [
                    self._read_table_file(v.path).assign(sim_day=v.sim_day)
                    for v in self._file_finder.table_by_simday(varname)
                ]
            )
            .reset_index(drop=True)
            .loc[:, ["sim_day", "key", "value"]]
        )

    def network(
        self, network_name: str, is_directed: bool = True, sim_day: Optional[int] = None
    ) -> nx.Graph:
        if sim_day is None:
            sim_day = self.dates().iloc[-1]["sim_day"]
        filepath = self._file_finder.network(network_name, sim_day)
        file_data = nx.nx_pydot.read_dot(filepath)
        # When support for FRED 10 is dropped, we will no longer need
        # the is_directed parameter and can use the following code instead:
        # if isinstance(file_data, nx.MultiDiGraph):
        if is_directed:
            return nx.DiGraph(file_data, name=network_name)
        else:
            return nx.Graph(file_data, name=network_name)

    def __repr__(self):
        return f"RunResultsF11({self._file_finder})"


class RunResultsFactory:
    def __init__(self, file_finder: Union[FileFinderF10, FileFinderF11]):
        self.file_finder = file_finder

    def build(self) -> RunResults:
        """Obtain a RunStatus appropriate for the given output directory.

        Raises
        ------
        TypeError
            If given `file_finder` is not a recognized type.
        """
        # TODO: Reduce code duplication across this and RunStatusFactory
        if self._is_legacy_file_finder(self.file_finder):
            return RunResultsF10(self.file_finder)
        elif self._is_file_finder(self.file_finder):
            return RunResultsF11(self.file_finder)
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
