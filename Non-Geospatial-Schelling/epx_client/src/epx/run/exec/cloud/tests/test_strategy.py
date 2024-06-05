from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import requests

from epx.synthpop import SynthPop, SynthPopModel
from epx.run.exec.cloud.strategy import (
    RunExecuteCloudStrategy,
    UnauthorizedUserError,
    _RunRequestPayload,
    _FREDArg,
    _FREDArgsBuilder,
    _RunResponseBody,
    _RunRequest,
    _RunResponse,
    _RunError,
    RunConfigError,
)
from epx.run.exec.common import RunParameters


@pytest.fixture
def sample_run_params() -> RunParameters:
    return RunParameters(
        Path("/home/epx/my-model/main.fred"),
        SynthPop("US_2010.v5", ["Location1", "Location2"]),
        date(2024, 1, 1),
        date(2024, 2, 29),
        model_params={"var1": 10.1, "var2": 40},
        seed=42,
    )


@pytest.fixture
def sample_synth_pop() -> SynthPopModel:
    return SynthPopModel(version="US_2010.v5", locations=["Location1", "Location2"])


@pytest.fixture
def sample_fred_args(sample_empty_output_dir) -> list[_FREDArg]:
    return [
        _FREDArg(flag="-p", value="/home/epx/my-model/main.fred"),
        _FREDArg(flag="-d", value=str(sample_empty_output_dir)),
        _FREDArg(flag="-o", value="var1=10.1"),
        _FREDArg(flag="-o", value="var2=40"),
        _FREDArg(flag="-s", value="42"),
        _FREDArg(flag="--start-date", value="2024-01-01"),
        _FREDArg(flag="--end-date", value="2024-02-29"),
        _FREDArg(flag="-l", value="Location1"),
        _FREDArg(flag="-l", value="Location2"),
    ]


@pytest.fixture
def sample_run_request_payload(
    sample_synth_pop, sample_fred_args
) -> _RunRequestPayload:
    return _RunRequestPayload(
        run_requests=[
            _RunRequest(
                working_dir="/home/epx/my-model",
                size="small2",
                fred_version="11.0.1",
                population=sample_synth_pop,
                fred_args=sample_fred_args,
            )
        ]
    )


@pytest.fixture
def sample_run_response_body_success(sample_run_request_payload) -> _RunResponseBody:
    return _RunResponseBody(
        run_responses=[
            _RunResponse(
                run_id=42,
                status="Submitted",
                run_request=sample_run_request_payload.run_requests[0],
            )
        ]
    )


@pytest.fixture
def sample_run_response_body_error(sample_run_request_payload) -> _RunResponseBody:
    return _RunResponseBody(
        run_responses=[
            _RunResponse(
                run_id=42,
                status="Failed",
                errors=[
                    _RunError(key="size", error="The compute size provided is invalid")
                ],
                run_request=sample_run_request_payload.run_requests[0],
            )
        ]
    )


@pytest.fixture
def sample_request_header() -> dict:
    return {
        "Authorization": "Bearer XYZ",
        "content-type": "application/json",
        "fredcli-version": "0.4.0",
    }


def test_run_request_payload(sample_run_request_payload, sample_empty_output_dir):
    assert (
        sample_run_request_payload.model_dump_json(by_alias=True, indent=2)
        == f"""
{{
  "runRequests": [
    {{
      "workingDir": "/home/epx/my-model",
      "size": "small2",
      "fredVersion": "11.0.1",
      "population": {{
        "version": "US_2010.v5",
        "locations": [
          "Location1",
          "Location2"
        ]
      }},
      "fredArgs": [
        {{
          "flag": "-p",
          "value": "/home/epx/my-model/main.fred"
        }},
        {{
          "flag": "-d",
          "value": "{str(sample_empty_output_dir)}"
        }},
        {{
          "flag": "-o",
          "value": "var1=10.1"
        }},
        {{
          "flag": "-o",
          "value": "var2=40"
        }},
        {{
          "flag": "-s",
          "value": "42"
        }},
        {{
          "flag": "--start-date",
          "value": "2024-01-01"
        }},
        {{
          "flag": "--end-date",
          "value": "2024-02-29"
        }},
        {{
          "flag": "-l",
          "value": "Location1"
        }},
        {{
          "flag": "-l",
          "value": "Location2"
        }}
      ]
    }}
  ]
}}
""".strip()
    )


def test_run_response_body(sample_run_response_body_error, sample_empty_output_dir):
    assert (
        sample_run_response_body_error.model_dump_json(by_alias=True, indent=2)
        == f"""
{{
  "runResponses": [
    {{
      "runId": 42,
      "status": "Failed",
      "errors": [
        {{
          "key": "size",
          "error": "The compute size provided is invalid"
        }}
      ],
      "runRequest": {{
        "workingDir": "/home/epx/my-model",
        "size": "small2",
        "fredVersion": "11.0.1",
        "population": {{
          "version": "US_2010.v5",
          "locations": [
            "Location1",
            "Location2"
          ]
        }},
        "fredArgs": [
          {{
            "flag": "-p",
            "value": "/home/epx/my-model/main.fred"
          }},
          {{
            "flag": "-d",
            "value": "{str(sample_empty_output_dir)}"
          }},
          {{
            "flag": "-o",
            "value": "var1=10.1"
          }},
          {{
            "flag": "-o",
            "value": "var2=40"
          }},
          {{
            "flag": "-s",
            "value": "42"
          }},
          {{
            "flag": "--start-date",
            "value": "2024-01-01"
          }},
          {{
            "flag": "--end-date",
            "value": "2024-02-29"
          }},
          {{
            "flag": "-l",
            "value": "Location1"
          }},
          {{
            "flag": "-l",
            "value": "Location2"
          }}
        ]
      }}
    }}
  ]
}}
""".strip()
    )


@patch("epx.run.exec.cloud.strategy.platform_api_headers")
@patch("epx.run.exec.cloud.strategy.Path.cwd")
@patch("epx.run.exec.cloud.strategy.requests.post")
def test_run_execute_cloud_strategy_success(
    mock_post,
    mock_cwd,
    mock_platform_api_headers,
    sample_run_params,
    sample_empty_output_dir,
    sample_run_request_payload,
    sample_run_response_body_success,
    sample_request_header,
):
    mock_response = Mock(
        spec=requests.Response,
        status_code=201,
        text=sample_run_response_body_success.model_dump_json(by_alias=True),
    )
    mock_post.return_value = mock_response
    mock_cwd.return_value = Path("/home/epx/my-model")

    mock_platform_api_headers.return_value = sample_request_header

    execute_strategy = RunExecuteCloudStrategy(
        sample_run_params, sample_empty_output_dir, size="small2", fred_version="11.0.1"
    )
    execute_strategy.execute()
    mock_post.assert_called_once_with(
        "https://studio.epistemix.cloud/v1/runs",
        headers=sample_request_header,
        data=sample_run_request_payload.model_dump_json(by_alias=True),
    )


@patch("epx.run.exec.cloud.strategy.platform_api_headers")
@patch("epx.run.exec.cloud.strategy.Path.cwd")
@patch("epx.run.exec.cloud.strategy.requests.post")
def test_run_execute_cloud_strategy_failed(
    mock_post,
    mock_cwd,
    mock_platform_api_headers,
    sample_run_params,
    sample_empty_output_dir,
    sample_run_request_payload,
    sample_run_response_body_error,
    sample_request_header,
):
    """Test that error is raised if API reports a user error."""
    mock_response = Mock(
        spec=requests.Response,
        status_code=201,
        text=sample_run_response_body_error.model_dump_json(by_alias=True),
    )
    mock_post.return_value = mock_response
    mock_cwd.return_value = Path("/home/epx/my-model")

    mock_platform_api_headers.return_value = sample_request_header

    execute_strategy = RunExecuteCloudStrategy(
        sample_run_params, sample_empty_output_dir, size="small2", fred_version="11.0.1"
    )

    with pytest.raises(RunConfigError) as e:
        execute_strategy.execute()
        mock_post.assert_called_once_with(
            "https://studio.epistemix.cloud/v1/runs",
            headers=sample_request_header,
            data=sample_run_request_payload.model_dump_json(by_alias=True),
        )
        assert e.message == "size error: The compute size provided is invalid"


@patch("epx.run.exec.cloud.strategy.platform_api_headers")
@patch("epx.run.exec.cloud.strategy.requests.post")
def test_run_execute_cloud_strategy_unauthorized(
    mock_post,
    mock_platform_api_headers,
    sample_run_params,
    sample_empty_output_dir,
    sample_request_header,
):
    """Test that if response is 403 Forbidden the correct error is thrown.

    An UnauthorizedUserError indicates the user is not authorized to use
    FRED Cloud.
    """
    mock_response = Mock(
        spec=requests.Response,
        status_code=403,
        ok=False,
        text='{"description": "Unauthorized error detail."}',
    )
    mock_post.return_value = mock_response

    mock_platform_api_headers.return_value = sample_request_header

    execute_strategy = RunExecuteCloudStrategy(
        sample_run_params, sample_empty_output_dir, size="small2", fred_version="11.0.1"
    )
    with pytest.raises(
        UnauthorizedUserError, match="Authorization error: Unauthorized error detail."
    ):
        execute_strategy.execute()


@patch("epx.run.exec.cloud.strategy.requests.post")
def test_run_execute_cloud_strategy_server_error(
    mock_post, sample_run_params, sample_empty_output_dir
):
    """Test that if response is 5XX Server Error the correct error is thrown.

    A RuntimeError indicates a server error has occurred. We may add more
    specialized errors over time, but in general a 5XX error is not something
    the user can do anything about.
    """
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    execute_strategy = RunExecuteCloudStrategy(
        sample_run_params, sample_empty_output_dir, size="small2", fred_version="11.0.1"
    )
    with pytest.raises(RuntimeError):
        execute_strategy.execute()


def test_fred_args_builder_fred11(sample_run_params):
    output_dir = "/home/epx/results"
    expected_args = [
        _FREDArg(flag="-p", value="/home/epx/my-model/main.fred"),
        _FREDArg(flag="-d", value=output_dir),
        _FREDArg(flag="-o", value="var1=10.1"),
        _FREDArg(flag="-o", value="var2=40"),
        _FREDArg(flag="-s", value="42"),
        _FREDArg(flag="--start-date", value="2024-01-01"),
        _FREDArg(flag="--end-date", value="2024-02-29"),
        _FREDArg(flag="-l", value="Location1"),
        _FREDArg(flag="-l", value="Location2"),
    ]

    args = (
        _FREDArgsBuilder("11.0.1")
        .program(sample_run_params.program)
        .output_dir(Path(output_dir))
        .overrides(sample_run_params.model_params)
        .seed(sample_run_params.seed)
        .start_date(sample_run_params.start_date)
        .end_date(sample_run_params.end_date)
        .locations(sample_run_params.synth_pop.locations)
        .build()
    )

    assert args == expected_args


def test_fred_args_builder_fred10(sample_run_params):
    output_dir = "/home/epx/results"
    # No locations flags for FRED 10 as this was only added in 11.
    expected_args = [
        _FREDArg(flag="-p", value="/home/epx/my-model/main.fred"),
        _FREDArg(flag="-d", value=output_dir),
        _FREDArg(flag="-o", value="var1=10.1"),
        _FREDArg(flag="-o", value="var2=40"),
        _FREDArg(flag="-r", value="42"),
        _FREDArg(flag="--start-date", value="2024-01-01"),
        _FREDArg(flag="--end-date", value="2024-02-29"),
    ]

    args = (
        _FREDArgsBuilder("10.1.1")
        .program(sample_run_params.program)
        .output_dir(Path(output_dir))
        .overrides(sample_run_params.model_params)
        .seed(sample_run_params.seed)
        .start_date(sample_run_params.start_date)
        .end_date(sample_run_params.end_date)
        .locations(sample_run_params.synth_pop.locations)
        .build()
    )

    assert args == expected_args
