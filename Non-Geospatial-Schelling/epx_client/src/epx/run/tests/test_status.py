import pandas as pd

from epx.run.fs import FileFinderF11, FileFinderF10
from epx.run.status import RunStatusF11, RunStatusF10, RunStatusFactory


def test_parse_legacy_not_started_status(sample_run_output_dir):
    # NB not-started directory doesn't exist. The non-existence of the output
    # directory is used as the indicator for epx_client that the run has not
    # started yet.
    not_started_ff = FileFinderF10(sample_run_output_dir("10.1.0") / "not-started", 1)
    not_started_rs = RunStatusF10(not_started_ff)

    assert not_started_rs.name == "NOT STARTED"
    assert str(not_started_rs) == "NOT STARTED"

    assert isinstance(not_started_rs.logs, pd.DataFrame)
    assert len(not_started_rs.logs.index) == 0


def test_parse_legacy_running_status(sample_run_output_dir):
    running_ff = FileFinderF10(sample_run_output_dir("10.1.0") / "running")
    running_rs = RunStatusF10(running_ff)

    assert running_rs.name == "RUNNING"
    assert str(running_rs) == "RUNNING"

    assert isinstance(running_rs.logs, pd.DataFrame)
    assert isinstance(running_rs.logs.iloc[0], pd.Series)


def test_parse_legacy_running_status_empty_return_code(sample_run_output_dir):
    """Handle the case where the return code file has been created, but not yet
    populated.
    """
    running_ff = FileFinderF10(
        sample_run_output_dir("10.1.0") / "running-empty-return-code"
    )
    running_rs = RunStatusF10(running_ff)

    assert running_rs.name == "RUNNING"
    assert str(running_rs) == "RUNNING"

    assert isinstance(running_rs.logs, pd.DataFrame)
    assert isinstance(running_rs.logs.iloc[0], pd.Series)


def test_parse_legacy_done_status(sample_run_output_dir):
    success_ff = FileFinderF10(sample_run_output_dir("10.1.0") / "success")
    success_rs = RunStatusF10(success_ff)

    assert repr(success_rs) == f"RunStatusF10({success_ff})"
    assert success_rs.name == "DONE"
    assert str(success_rs) == "DONE"

    assert isinstance(success_rs.logs, pd.DataFrame)
    assert isinstance(success_rs.logs.iloc[0], pd.Series)
    info_logs = success_rs.logs.pipe(lambda df: df[df["level"] != "ERROR"])
    assert len(info_logs.index) > 1
    assert info_logs.iloc[0]["level"] == "INFO"
    assert isinstance(info_logs.iloc[0]["time"], pd.Timestamp)
    assert info_logs.iloc[0]["message"] == "Environment variables:"
    assert info_logs.iloc[-1]["message"] == "FRED exiting with code 0"


def test_parse_legacy_error_status(sample_run_output_dir):
    error_ff = FileFinderF10(sample_run_output_dir("10.1.0") / "error")
    error_rs = RunStatusF10(error_ff)

    assert error_rs.name == "ERROR"
    assert str(error_rs) == "ERROR"

    assert isinstance(error_rs.logs, pd.DataFrame)
    assert isinstance(error_rs.logs.iloc[0], pd.Series)
    error_logs = error_rs.logs.pipe(lambda df: df[df["level"] == "ERROR"])
    assert len(error_logs.index) == 1
    assert error_logs.iloc[0]["level"] == "ERROR"
    assert isinstance(error_logs.iloc[0]["time"], pd.Timestamp)
    assert error_logs.iloc[0]["message"] == (
        "Agent 204941490 aborts in condition TRANS_CONDITION state "
        "Susceptible on sim day 0 sim date 2020-01-01:\nabort()"
    )


def test_parse_not_started_status(sample_run_output_dir):
    # NB not-started directory doesn't exist. The non-existence of the output
    # directory is used as the indicator for epx_client that the run has not
    # started yet.
    not_started_ff = FileFinderF11(sample_run_output_dir("11.0.0") / "not-started")
    not_started_rs = RunStatusF11(not_started_ff)

    assert not_started_rs.name == "NOT STARTED"
    assert str(not_started_rs) == "NOT STARTED"

    assert isinstance(not_started_rs.logs, pd.DataFrame)
    assert len(not_started_rs.logs.index) == 0


def test_parse_running_status(sample_run_output_dir):
    running_ff = FileFinderF11(sample_run_output_dir("11.0.0") / "running")
    running_rs = RunStatusF11(running_ff)

    assert running_rs.name == "RUNNING"
    assert str(running_rs) == "RUNNING"

    assert isinstance(running_rs.logs, pd.DataFrame)
    assert isinstance(running_rs.logs.iloc[0], pd.Series)


def test_parse_running_status_empty_return_code(sample_run_output_dir):
    """Handle the case where the return code file has been created, but not yet
    populated.
    """
    running_ff = FileFinderF11(
        sample_run_output_dir("11.0.0") / "running-empty-return-code"
    )
    running_rs = RunStatusF11(running_ff)

    assert running_rs.name == "RUNNING"
    assert str(running_rs) == "RUNNING"

    assert isinstance(running_rs.logs, pd.DataFrame)
    assert isinstance(running_rs.logs.iloc[0], pd.Series)


def test_parse_done_status(sample_run_output_dir):
    success_ff = FileFinderF11(sample_run_output_dir("11.0.0") / "success")
    success_rs = RunStatusF11(success_ff)

    assert repr(success_rs) == f"RunStatusF11({success_ff})"
    assert success_rs.name == "DONE"
    assert str(success_rs) == "DONE"

    assert isinstance(success_rs.logs, pd.DataFrame)
    assert isinstance(success_rs.logs.iloc[0], pd.Series)
    info_logs = success_rs.logs.pipe(lambda df: df[df["level"] != "ERROR"])
    assert len(info_logs.index) > 1
    assert info_logs.iloc[0]["level"] == "INFO"
    assert isinstance(info_logs.iloc[0]["time"], pd.Timestamp)
    assert (
        info_logs.iloc[0]["message"]
        == "Environment variables: FRED_DATA=/data FRED_LIBRARY=/library"
    )
    assert info_logs.iloc[-1]["message"] == "FRED exiting with code 0"


def test_parse_error_status(sample_run_output_dir):
    error_ff = FileFinderF11(sample_run_output_dir("11.0.0") / "error")
    error_rs = RunStatusF11(error_ff)

    assert error_rs.name == "ERROR"
    assert str(error_rs) == "ERROR"

    assert isinstance(error_rs.logs, pd.DataFrame)
    assert isinstance(error_rs.logs.iloc[0], pd.Series)
    error_logs = error_rs.logs.pipe(lambda df: df[df["level"] == "ERROR"])
    assert len(error_logs.index) == 1
    assert error_logs.iloc[0]["level"] == "ERROR"
    assert isinstance(error_logs.iloc[0]["time"], pd.Timestamp)
    assert error_logs.iloc[0]["message"] == (
        "Agent 204941490 aborts in condition TRANS_CONDITION state "
        "Susceptible on sim day 0 sim date 2020-01-01: abort()"
    )


def test_run_status_factory(sample_run_output_dir):
    legacy_ff = FileFinderF10(sample_run_output_dir("10.1.0") / "success")
    ff = FileFinderF11(sample_run_output_dir("11.0.0") / "success")

    assert isinstance(RunStatusFactory(legacy_ff).build(), RunStatusF10)
    assert isinstance(RunStatusFactory(ff).build(), RunStatusF11)
