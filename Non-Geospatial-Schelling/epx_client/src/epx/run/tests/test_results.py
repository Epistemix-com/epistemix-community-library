import pytest

import pandas as pd
from pandas.api.types import is_numeric_dtype
import networkx as nx

import pandera as pa

from epx.run.fs import FileFinderF10, FileFinderF11
from epx.run.results import RunResultsF10, RunResultsF11, RunResultsFactory


@pytest.fixture(scope="session")
def state_count_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "count": pa.Column(int, checks=pa.Check.ge(0)),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def state_new_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "new": pa.Column(int, checks=pa.Check.ge(0)),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def state_cumulative_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "cumulative": pa.Column(int, checks=pa.Check.ge(0)),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def pop_size_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "pop_size": pa.Column(int, checks=pa.Check.ge(0)),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def epi_weeks_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "epi_week": pa.Column(
                str, checks=pa.Check.str_matches(r"^[0-9]{4}\.[0-9]{2}$")
            ),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def dates_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "sim_date": pa.Column(pd.Timestamp),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def print_output_schema():
    return pa.SeriesSchema(
        str,
        nullable=False,
        unique=False,
        name="print_output",
    )


@pytest.fixture(scope="session")
def file_output_schema():
    return pa.SeriesSchema(
        str,
        nullable=False,
        unique=False,
        name="file_output",
    )


@pytest.fixture(scope="session")
def numeric_var_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "value": pa.Column(float),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def list_var_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "list_index": pa.Column(int, checks=pa.Check.ge(0)),
            "value": pa.Column(float),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def list_var_wide_schema():
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "item_[0-9]*": pa.Column(float, regex=True, nullable=True),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def list_table_var_schema():
    is_number = pa.Check(is_numeric_dtype, name="is_number")
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "key": pa.Column(checks=is_number),
            "list_index": pa.Column(int, checks=pa.Check.ge(0)),
            "value": pa.Column(checks=is_number),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def list_table_var_wide_schema():
    is_number = pa.Check(is_numeric_dtype, name="is_number")
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "key": pa.Column(checks=is_number),
            "item_[0-9]*": pa.Column(float, regex=True, nullable=True),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="session")
def table_var_schema():
    is_number = pa.Check(is_numeric_dtype, name="is_number")
    return pa.DataFrameSchema(
        {
            "sim_day": pa.Column(int, checks=pa.Check.ge(0)),
            "key": pa.Column(checks=is_number),
            "value": pa.Column(float),
        },
        strict=True,
        ordered=True,
    )


@pytest.fixture(scope="function")
def fred10_run_results(sample_run_output_dir):
    output_dir = sample_run_output_dir("10.1.0") / "success"
    ff = FileFinderF10(output_dir)
    return RunResultsF10(ff)


@pytest.fixture(scope="function")
def fred11_run_results(sample_run_output_dir):
    output_dir = sample_run_output_dir("11.0.0") / "success"
    ff = FileFinderF11(output_dir)
    return RunResultsF11(ff)


def test_fred10_state_count(fred10_run_results, state_count_schema):
    df = fred10_run_results.state("TRANS_CONDITION", "Excluded", "count")
    state_count_schema.validate(df)


def test_fred10_state_new(fred10_run_results, state_new_schema):
    df = fred10_run_results.state("TRANS_CONDITION", "Excluded", "new")
    state_new_schema.validate(df)


def test_fred10_state_cumulative(fred10_run_results, state_cumulative_schema):
    df = fred10_run_results.state("TRANS_CONDITION", "Excluded", "cumulative")
    state_cumulative_schema.validate(df)


def test_fred10_pop_size(fred10_run_results, pop_size_schema):
    df = fred10_run_results.pop_size()
    pop_size_schema.validate(df)


def test_fred10_epi_weeks(fred10_run_results, epi_weeks_schema):
    df = fred10_run_results.epi_weeks()
    epi_weeks_schema.validate(df)


def test_fred10_dates(fred10_run_results, dates_schema):
    df = fred10_run_results.dates()
    dates_schema.validate(df)


def test_fred10_print_output(fred10_run_results, print_output_schema):
    s = fred10_run_results.print_output()
    print_output_schema.validate(s)


def test_fred10_csv_output(fred10_run_results):
    # No schema for csv output as this is user-specified
    df = fred10_run_results.csv_output("sample.csv")
    assert isinstance(df, pd.DataFrame)


def test_fred10_file_output(fred10_run_results, file_output_schema):
    s = fred10_run_results.file_output("sample_file.txt")
    file_output_schema.validate(s)


def test_fred10_numeric_var(fred10_run_results, numeric_var_schema):
    df = fred10_run_results.numeric_var("sample_numeric")
    numeric_var_schema.validate(df)


def test_fred10_list_var(fred10_run_results, list_var_schema):
    df = fred10_run_results.list_var("sample_list")
    list_var_schema.validate(df)


def test_fred10_list_var_wide(fred10_run_results, list_var_wide_schema):
    df = fred10_run_results.list_var("sample_list", wide=True)
    list_var_wide_schema.validate(df)


def test_fred10_list_table_var(fred10_run_results, list_table_var_schema):
    df = fred10_run_results.list_table_var("sample_list_table")
    list_table_var_schema.validate(df)


def test_fred10_list_table_var_wide(fred10_run_results, list_table_var_wide_schema):
    df = fred10_run_results.list_table_var("sample_list_table", wide=True)
    list_table_var_wide_schema.validate(df)


def test_fred10_table_var(fred10_run_results, table_var_schema):
    df = fred10_run_results.table_var("sample_table")
    table_var_schema.validate(df)


def test_fred10_network(fred10_run_results):
    d_end = fred10_run_results.network("directed")
    assert isinstance(d_end, nx.classes.digraph.DiGraph)
    assert d_end.number_of_nodes() == 6
    assert d_end.number_of_edges() == 0

    d_2 = fred10_run_results.network("directed", sim_day=2)
    assert isinstance(d_2, nx.classes.digraph.DiGraph)
    assert d_2.number_of_nodes() == 6
    assert d_2.number_of_edges() == 2

    u_end = fred10_run_results.network("undirected", is_directed=False)
    assert isinstance(u_end, nx.classes.graph.Graph)
    assert u_end.number_of_nodes() == 6
    assert u_end.number_of_edges() == 0

    u_2 = fred10_run_results.network("undirected", is_directed=False, sim_day=2)
    assert isinstance(u_2, nx.classes.graph.Graph)
    assert u_2.number_of_nodes() == 6
    assert u_2.number_of_edges() == 1


def test_fred11_state_count(fred11_run_results, state_count_schema):
    df = fred11_run_results.state("TRANS_CONDITION", "Excluded", "count")
    state_count_schema.validate(df)


def test_fred11_state_new(fred11_run_results, state_new_schema):
    df = fred11_run_results.state("TRANS_CONDITION", "Excluded", "new")
    state_new_schema.validate(df)


def test_fred11_state_cumulative(fred11_run_results, state_cumulative_schema):
    df = fred11_run_results.state("TRANS_CONDITION", "Excluded", "cumulative")
    state_cumulative_schema.validate(df)


def test_fred11_pop_size(fred11_run_results, pop_size_schema):
    df = fred11_run_results.pop_size()
    pop_size_schema.validate(df)


def test_fred11_epi_weeks(fred11_run_results, epi_weeks_schema):
    df = fred11_run_results.epi_weeks()
    epi_weeks_schema.validate(df)


def test_fred11_dates(fred11_run_results, dates_schema):
    df = fred11_run_results.dates()
    dates_schema.validate(df)


def test_fred11_print_output(fred11_run_results, print_output_schema):
    s = fred11_run_results.print_output()
    print_output_schema.validate(s)


def test_fred11_csv_output(fred11_run_results):
    # No schema for csv output as this is user-specified
    df = fred11_run_results.csv_output("sample.csv")
    assert isinstance(df, pd.DataFrame)


def test_fred11_file_output(fred11_run_results, file_output_schema):
    s = fred11_run_results.file_output("sample_file.txt")
    file_output_schema.validate(s)


def test_fred11_numeric_var(fred11_run_results, numeric_var_schema):
    df = fred11_run_results.numeric_var("sample_numeric")
    numeric_var_schema.validate(df)


def test_fred11_list_var(fred11_run_results, list_var_schema):
    df = fred11_run_results.list_var("sample_list")
    list_var_schema.validate(df)


def test_fred11_list_var_wide(fred11_run_results, list_var_wide_schema):
    df = fred11_run_results.list_var("sample_list", wide=True)
    list_var_wide_schema.validate(df)


def test_fred11_list_table_var(fred11_run_results, list_table_var_schema):
    df = fred11_run_results.list_table_var("sample_list_table")
    list_table_var_schema.validate(df)


def test_fred11_list_table_var_wide(fred11_run_results, list_table_var_wide_schema):
    df = fred11_run_results.list_table_var("sample_list_table", wide=True)
    list_table_var_wide_schema.validate(df)


def test_fred11_table_var(fred11_run_results, table_var_schema):
    df = fred11_run_results.table_var("sample_table")
    table_var_schema.validate(df)


def test_fred11_network(fred11_run_results):
    d_end = fred11_run_results.network("directed")
    assert isinstance(d_end, nx.classes.digraph.DiGraph)
    assert d_end.number_of_nodes() == 6
    assert d_end.number_of_edges() == 0

    d_2 = fred11_run_results.network("directed", sim_day=2)
    assert isinstance(d_2, nx.classes.digraph.DiGraph)
    assert d_2.number_of_nodes() == 6
    assert d_2.number_of_edges() == 2

    u_end = fred11_run_results.network("undirected", is_directed=False)
    assert isinstance(u_end, nx.classes.graph.Graph)
    assert u_end.number_of_nodes() == 6
    assert u_end.number_of_edges() == 0

    u_2 = fred11_run_results.network("undirected", is_directed=False, sim_day=2)
    assert isinstance(u_2, nx.classes.graph.Graph)
    assert u_2.number_of_nodes() == 6
    assert u_2.number_of_edges() == 1


def test_run_results_factory(sample_run_output_dir):
    fred10_ff = FileFinderF10(sample_run_output_dir("10.1.0") / "success")
    fred11_ff = FileFinderF11(sample_run_output_dir("11.0.0") / "success")

    assert isinstance(RunResultsFactory(fred10_ff).build(), RunResultsF10)
    assert isinstance(RunResultsFactory(fred11_ff).build(), RunResultsF11)
