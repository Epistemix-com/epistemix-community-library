from unittest.mock import Mock

import pytest

import numpy as np
import pandas as pd
import networkx as nx

from epx.run.results import RunResults
from epx.job.results import JobResults


@pytest.fixture
def mock_run_results() -> RunResults:
    return Mock(
        spec=RunResults,
        state=Mock(
            return_value=pd.DataFrame.from_records(
                [(0, 10), (1, 20)], columns=["sim_day", "count"]
            )
        ),
        pop_size=Mock(
            return_value=pd.DataFrame.from_records(
                [(0, 100), (1, 200)], columns=["sim_day", "pop_size"]
            )
        ),
        epi_weeks=Mock(
            return_value=pd.DataFrame.from_records(
                [(0, "2024.01"), (1, "2024.02")], columns=["sim_day", "epi_week"]
            )
        ),
        dates=Mock(
            return_value=pd.DataFrame.from_records(
                [(0, pd.Timestamp("2024-01-01")), (0, pd.Timestamp("2024-01-02"))],
                columns=["sim_day", "sim_date"],
            )
        ),
        print_output=Mock(
            return_value=pd.Series(["Output 1", "Output 2"], name="print_output")
        ),
        csv_output=Mock(
            return_value=pd.DataFrame.from_records(
                [(1, 2), (3, 4)], columns=["col1", "col2"]
            )
        ),
        file_output=Mock(
            return_value=pd.Series(
                pd.Series(["Output 1", "Output 2"], name="file_output")
            )
        ),
        numeric_var=Mock(
            return_value=pd.DataFrame.from_records(
                [(0, 40), (1, 41)], columns=["sim_day", "value"]
            )
        ),
        list_var=Mock(
            side_effect=_mock_list_var_return_value,
        ),
        list_table_var=Mock(
            side_effect=_mock_list_table_var_return_value,
        ),
        table_var=Mock(
            return_value=pd.DataFrame.from_records(
                [(0, 1.1, 10), (0, 2.2, 20), (1, 1.1, 30), (1, 2.2, 40)],
                columns=["sim_day", "key", "value"],
            )
        ),
        network=Mock(return_value=nx.Graph()),
    )


def _mock_list_var_return_value(_, wide=False):
    """Mocked list_var response depending on if wide format specified."""
    if wide:
        return pd.DataFrame.from_records(
            [
                (0, 10, 20),
                (1, 30, 40),
            ],
            columns=["sim_day", "item_0", "item_1"],
        )
    return pd.DataFrame.from_records(
        [
            (0, 0, 10),
            (0, 1, 20),
            (1, 0, 30),
            (1, 1, 40),
        ],
        columns=["sim_day", "list_index", "value"],
    )


def _mock_list_table_var_return_value(_, wide=False):
    """Mocked list_table_var response depending on if wide format specified."""
    if wide:
        return pd.DataFrame.from_records(
            [
                (0, 1.1, 10, np.nan),
                (0, 2.2, 20, 30),
                (1, 1.1, 40, np.nan),
                (1, 2.2, 50, 60),
            ],
            columns=["sim_day", "key", "item_0", "item_1"],
        )
    return pd.DataFrame.from_records(
        [
            (0, 1.1, 0, 10),
            (0, 2.2, 0, 20),
            (0, 2.2, 1, 30),
            (1, 1.1, 0, 40),
            (1, 2.2, 0, 50),
            (1, 2.2, 1, 60),
        ],
        columns=["sim_day", "key", "list_index", "value"],
    )


@pytest.fixture
def mock_run_results_with_ids(mock_run_results) -> list[tuple[int, RunResults]]:
    return [
        (1, mock_run_results),
        (2, mock_run_results),
    ]


def test_job_results_state(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.state("condition", "state", "count")
    assert df.equals(
        pd.DataFrame.from_records(
            [(1, 0, 10), (1, 1, 20), (2, 0, 10), (2, 1, 20)],
            columns=["run_id", "sim_day", "count"],
        )
    )


def test_job_results_pop_size(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.pop_size()
    assert df.equals(
        pd.DataFrame.from_records(
            [(1, 0, 100), (1, 1, 200), (2, 0, 100), (2, 1, 200)],
            columns=["run_id", "sim_day", "pop_size"],
        )
    )


def test_job_results_epi_weeks(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.epi_weeks()
    assert df.equals(
        pd.DataFrame.from_records(
            [
                (1, 0, "2024.01"),
                (1, 1, "2024.02"),
                (2, 0, "2024.01"),
                (2, 1, "2024.02"),
            ],
            columns=["run_id", "sim_day", "epi_week"],
        )
    )


def test_job_results_dates(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.dates()
    assert df.equals(
        pd.DataFrame.from_records(
            [
                (1, 0, pd.Timestamp("2024-01-01")),
                (1, 0, pd.Timestamp("2024-01-02")),
                (2, 0, pd.Timestamp("2024-01-01")),
                (2, 0, pd.Timestamp("2024-01-02")),
            ],
            columns=["run_id", "sim_day", "sim_date"],
        )
    )


def test_job_results_print_output(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.print_output()
    assert df.equals(
        pd.DataFrame.from_records(
            [(1, "Output 1"), (1, "Output 2"), (2, "Output 1"), (2, "Output 2")],
            columns=["run_id", "print_output"],
        )
    )


def test_job_results_csv_output(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.csv_output("sample.csv")
    assert df.equals(
        pd.DataFrame.from_records(
            [(1, 1, 2), (1, 3, 4), (2, 1, 2), (2, 3, 4)],
            columns=["run_id", "col1", "col2"],
        )
    )


def test_job_results_file_output(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.file_output("sample.txt")
    assert df.equals(
        pd.DataFrame.from_records(
            [(1, "Output 1"), (1, "Output 2"), (2, "Output 1"), (2, "Output 2")],
            columns=["run_id", "file_output"],
        )
    )


def test_job_results_numeric_var(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.numeric_var("my_var")
    assert df.equals(
        pd.DataFrame.from_records(
            [(1, 0, 40), (1, 1, 41), (2, 0, 40), (2, 1, 41)],
            columns=["run_id", "sim_day", "value"],
        )
    )


def test_job_results_list_var(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.list_var("my_list_var")
    assert df.equals(
        pd.DataFrame.from_records(
            [
                (1, 0, 0, 10),
                (1, 0, 1, 20),
                (1, 1, 0, 30),
                (1, 1, 1, 40),
                (2, 0, 0, 10),
                (2, 0, 1, 20),
                (2, 1, 0, 30),
                (2, 1, 1, 40),
            ],
            columns=["run_id", "sim_day", "list_index", "value"],
        )
    )


def test_job_results_list_var_wide(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.list_var("my_list_var", wide=True)
    assert df.equals(
        pd.DataFrame.from_records(
            [
                (1, 0, 10, 20),
                (1, 1, 30, 40),
                (2, 0, 10, 20),
                (2, 1, 30, 40),
            ],
            columns=["run_id", "sim_day", "item_0", "item_1"],
        )
    )


def test_job_results_list_table_var(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.list_table_var("my_list_table_var")
    assert df.equals(
        pd.DataFrame.from_records(
            [
                (1, 0, 1.1, 0, 10),
                (1, 0, 2.2, 0, 20),
                (1, 0, 2.2, 1, 30),
                (1, 1, 1.1, 0, 40),
                (1, 1, 2.2, 0, 50),
                (1, 1, 2.2, 1, 60),
                (2, 0, 1.1, 0, 10),
                (2, 0, 2.2, 0, 20),
                (2, 0, 2.2, 1, 30),
                (2, 1, 1.1, 0, 40),
                (2, 1, 2.2, 0, 50),
                (2, 1, 2.2, 1, 60),
            ],
            columns=["run_id", "sim_day", "key", "list_index", "value"],
        )
    )


def test_job_results_list_table_var_wide(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.list_table_var("my_list_table_var", wide=True)
    assert df.equals(
        pd.DataFrame.from_records(
            [
                (1, 0, 1.1, 10, np.nan),
                (1, 0, 2.2, 20, 30),
                (1, 1, 1.1, 40, np.nan),
                (1, 1, 2.2, 50, 60),
                (2, 0, 1.1, 10, np.nan),
                (2, 0, 2.2, 20, 30),
                (2, 1, 1.1, 40, np.nan),
                (2, 1, 2.2, 50, 60),
            ],
            columns=["run_id", "sim_day", "key", "item_0", "item_1"],
        )
    )


def test_job_results_table_var(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    df = job_results.table_var("my_table_var")
    assert df.equals(
        pd.DataFrame.from_records(
            [
                (1, 0, 1.1, 10),
                (1, 0, 2.2, 20),
                (1, 1, 1.1, 30),
                (1, 1, 2.2, 40),
                (2, 0, 1.1, 10),
                (2, 0, 2.2, 20),
                (2, 1, 1.1, 30),
                (2, 1, 2.2, 40),
            ],
            columns=["run_id", "sim_day", "key", "value"],
        )
    )


def test_job_results_network(mock_run_results_with_ids):
    job_results = JobResults(mock_run_results_with_ids)
    networks = job_results.network("my_network")
    assert isinstance(networks, pd.Series)
    assert len(networks) == 2
    assert isinstance(networks[1], nx.Graph)
