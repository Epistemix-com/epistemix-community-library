from pathlib import Path
import shutil
from unittest.mock import patch

import pytest

from epx.synthpop import SynthPop
from epx.run.exec.common import RunParameters
from epx.run.results import RunResultsF11
from epx.run.status import RunStatusF11
from epx.run.run import Run, _RunModel, RunExistsError


@pytest.fixture
def sample_run_params() -> RunParameters:
    return RunParameters(
        "main.fred",
        SynthPop("US_2010.v5", ["Location1", "Location2"]),
        "2024-01-01",
        "2024-02-29",
    )


@pytest.fixture(scope="function")
def temp_populated_output_dir(sample_empty_output_dir, sample_run_output_dir) -> Path:
    """Return a sample output directory populated with FRED 11.0.0 output.

    Tests are free to manipulate this data as required, with any changes
    discarded at the end of the test.
    """
    src_dir = sample_run_output_dir("11.0.0") / "success"
    shutil.copytree(src_dir, sample_empty_output_dir, dirs_exist_ok=True)
    return sample_empty_output_dir


@pytest.fixture
def temp_home_dir(tmpdir) -> Path:
    return Path(tmpdir.mkdir("home"))


def test_run_repr(sample_run_params, sample_empty_output_dir):
    run = Run(
        sample_run_params, sample_empty_output_dir, size="small2", fred_version="latest"
    )
    assert repr(run) == (
        f"Run("
        f"params={sample_run_params}, "
        f"output_dir={sample_empty_output_dir}, "
        f"size=small2, "
        f"fred_version=latest"
        f")"
    )


@patch("epx.run.run.Path.home")
@patch("epx.run.run.RunExecuteCloudStrategy")
def test_run_execute(
    mock_strategy, mock_home, temp_home_dir, sample_empty_output_dir, sample_run_params
):
    mock_home.return_value = temp_home_dir
    run = Run(
        sample_run_params, sample_empty_output_dir, size="small2", fred_version="latest"
    )
    run.execute()

    # Check mocked RunExecuteCloudStrategy constructor called as expected
    mock_strategy.assert_called_once_with(
        sample_run_params, sample_empty_output_dir, "small2", "latest"
    )
    # Check strategy's execute method called
    run._exec_strategy.execute.assert_called_once()

    # Test that run cache file is populated
    expected_run_cache_dir = (
        mock_home() / ".epx_client/runs" / str(sample_empty_output_dir)[1:]
    )
    assert expected_run_cache_dir.is_dir()
    expected_run_filepath = expected_run_cache_dir / "run.json"
    assert expected_run_filepath.is_file()
    with open(expected_run_filepath, "r") as f:
        run_cache_data = f.read()
    assert isinstance(_RunModel.model_validate_json(run_cache_data), _RunModel)


@patch("epx.run.run.Path.home")
def test_run_execute_error_if_run_exists(
    mock_home, temp_home_dir, sample_run_output_dir, sample_run_params
):
    mock_home.return_value = temp_home_dir
    # output_dir is populated with test data
    output_dir = sample_run_output_dir("11.0.0") / "success"
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")

    with pytest.raises(RunExistsError):
        run.execute()


@patch("epx.run.run.Path.home")
@patch("epx.run.run.RunExecuteCloudStrategy")
def test_from_output_dir(
    mock_strategy, mock_home, temp_home_dir, sample_empty_output_dir, sample_run_params
):
    """Test that after a (mock) run execution, a Run object can be re-read from
    cached data."""
    mock_home.return_value = temp_home_dir
    f11_output_dir = sample_empty_output_dir / "11.0.0"
    f11_output_dir.mkdir()
    run_f11 = Run(
        sample_run_params, f11_output_dir, size="small2", fred_version="11.0.0"
    )
    run_f11.execute()
    new_run_f11 = Run.from_output_dir(f11_output_dir)
    assert new_run_f11 == run_f11

    f10_output_dir = sample_empty_output_dir / "10.1.0"
    f10_output_dir.mkdir()
    run_f10 = Run(
        sample_run_params, f10_output_dir, size="small2", fred_version="10.1.0"
    )
    run_f10.execute()
    new_run_f10 = Run.from_output_dir(f10_output_dir)
    assert new_run_f10 == run_f10


def test_status(sample_run_output_dir, sample_empty_output_dir, sample_run_params):
    output_dir = sample_run_output_dir("11.0.0") / "success"
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")
    assert isinstance(run.status, RunStatusF11)

    output_dir = sample_empty_output_dir
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")
    assert str(run.status) == "RUNNING"  # Results directory exists, but not populated


def test_results(sample_run_output_dir, sample_empty_output_dir, sample_run_params):
    output_dir = sample_run_output_dir("11.0.0") / "success"
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")
    assert isinstance(run.results, RunResultsF11)

    # Should be None if output_dir not populated
    output_dir = sample_empty_output_dir
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")
    assert run.results is None


@patch("epx.run.run.input", return_value="y")
def test_delete_user_confirm(mock_input, sample_run_params, temp_populated_output_dir):
    """Test case where user interactively confirms that run data should be
    deleted.
    """
    output_dir = temp_populated_output_dir
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")
    assert len([x for x in output_dir.glob("*")]) > 0
    run.delete()
    mock_input.assert_called_once_with(f"Delete contents of {output_dir}? [y/N]")
    assert not output_dir.exists()
    assert len([x for x in output_dir.glob("*")]) == 0


@patch("epx.run.run.input", return_value="n")
def test_delete_user_reject(mock_input, sample_run_params, temp_populated_output_dir):
    """Test case where user interactively denies that run data should be
    deleted.
    """
    output_dir = temp_populated_output_dir
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")
    n_files = len([x for x in output_dir.glob("*")])
    assert n_files > 0
    run.delete()
    mock_input.assert_called_once_with(f"Delete contents of {output_dir}? [y/N]")
    assert output_dir.is_dir()
    assert len([x for x in output_dir.glob("*")]) == n_files


def test_delete_non_interactive(sample_run_params, temp_populated_output_dir):
    """Test case where ``interactive=False`` causes run data to be deleted
    without interactive user confirmation.
    """
    output_dir = temp_populated_output_dir
    run = Run(sample_run_params, output_dir, size="small2", fred_version="latest")
    n_files = len([x for x in output_dir.glob("*")])
    assert n_files > 0
    run.delete(interactive=False)
    assert not output_dir.exists()
