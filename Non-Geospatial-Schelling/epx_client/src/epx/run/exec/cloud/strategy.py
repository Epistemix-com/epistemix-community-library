"""Implementation for running FRED jobs using the Platform IDE.

The cloud execution strategy is implemented by the ``RunExecuteCloudStrategy``
class defined here. This class conforms to the ``RunExecuteStrategy``
interface.
"""

from datetime import date
import logging
from pathlib import Path
from typing import Literal, Optional, Union

import requests

from pydantic import BaseModel, ConfigDict, Field

from epx.synthpop import SynthPopModel
from epx.run.exec.common import RunExecuteStrategy, RunParameters
from epx.run.exec.compat import fred_major_version
from epx.run.exec.cloud.auth import platform_api_headers
from epx.run.exec.cloud.config import api_base_url

logger = logging.getLogger(__name__)


class _FREDArg(BaseModel):
    """A FRED command line argument/ value pair.

    Attributes
    ----------
    flag : str
        The command line flag to pass to FRED, e.g. ``-p``.
    value : str
        The value corresponding to the command line flag, e.g.
        ``my-model/main.fred``.
    """

    flag: str
    value: str


class _RunRequest(BaseModel):
    """Configuration for an individual run to be executed.

    Attributes
    ----------
    working_dir : str
        Working directory that FRED should be called from. This ensures
        that e.g relative paths within the model code are resolved correctly.
    size : str
        Name of instance size to use for the run.
    fred_version : str
        Version of FRED to use for the run.
    population : SynthPopModel
        The specific locations within a synthetic population that should be
        used for the simulation.
    fred_args : list[_FREDArg]
        Command line arguments to be passed to FRED.
    """

    model_config = ConfigDict(populate_by_name=True)

    working_dir: str = Field(alias="workingDir")
    size: str
    fred_version: str = Field(alias="fredVersion")
    population: SynthPopModel
    fred_args: list[_FREDArg] = Field(alias="fredArgs")


class _RunRequestPayload(BaseModel):
    """The complete run request object passed to FRED Cloud.

    Attributes
    ----------
    run_requests : list[_RunRequest]
        Collection of individual run request configurations.
    """

    model_config = ConfigDict(populate_by_name=True)

    run_requests: list[_RunRequest] = Field(alias="runRequests")


class _RunError(BaseModel):
    """A run configuration error in FRED Cloud responses.

    Attributes
    ----------
    key : str
        The general category of the error reported by FRED Cloud API, e.g.
        ``size`` for errors related to instance size, or ``fredVersion`` if the
        specified FRED version is not recognized.
    error : str
        Detailed description of the error.
    """

    key: str
    error: str


class _RunResponse(BaseModel):
    """Response object from the /runs endpoint for an individual run.

    Attributes
    ----------
    run_id : int
        Unique ID for the run.
    status : Literal["Submitted", "Failed"]
        Textual description of the status of the run.
    errors : list[_RunError], optional
        List of any errors in the run configuration identified by the API
    run_request : _RunRequestPayload
        A copy of the originating request object that the response relates to.
    """

    model_config = ConfigDict(populate_by_name=True)

    run_id: int = Field(alias="runId")
    status: Literal["Submitted", "Failed"]
    errors: Optional[list[_RunError]] = None
    run_request: _RunRequest = Field(alias="runRequest")


class _RunResponseBody(BaseModel):
    """Response object for a batch of submitted runs from the /runs endpoint.

    Attributes
    ----------
    run_responses : list[_RunResponse]
        Collection of responses for individual runs in the originating
        request.
    """

    model_config = ConfigDict(populate_by_name=True)

    run_responses: list[_RunResponse] = Field(alias="runResponses")


class _ForbiddenResponse(BaseModel):
    """Response object for a 403 Forbidden response from the SRS."""

    description: str


class RunExecuteCloudStrategy(RunExecuteStrategy):
    """Strategy for submitting an individual run to execute on FRED Cloud.

    Encapsulates logic for forming a request that is compatible with the FRED
    Cloud API /run endpoint based on user input, submitting that request
    to FRED Cloud, and converting any errors reported by FRED Cloud into Python
    exceptions.

    Parameters
    ----------
    params : RunParameters
        Parameters to be passed to FRED configuring the run.
    output_dir : Path
        Directory in the user's environment to write run results to.
    size : str
        Name of instance size to use for the run.
    fred_version : str
        Version of FRED to use for the run.

    Attributes
    ----------
    params : RunParameters
        Parameters to be passed to FRED configuring the run.
    output_dir : Path
        Directory in the user's environment to write run results to.
    size : str
        Name of instance size to use for the run.
    fred_version : str
        Version of FRED to use for the run.
    """

    def __init__(
        self, params: RunParameters, output_dir: Path, size: str, fred_version: str
    ):
        self.params = params
        self.output_dir = output_dir
        self.size = size
        self.fred_version = fred_version

    def execute(self) -> None:
        """Submit a run to FRED Cloud.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        IndexError
            If the FRED Cloud response unexpectedly implies the submission of
            multiple runs.
        RunConfigError
            If FRED Cloud reports an issue with the user's request.
        """
        endpoint_url = f"{api_base_url()}/runs"
        # Post request for a run to be executed to FRED Cloud API
        payload = self._request_payload().model_dump_json(by_alias=True)
        logger.debug(f"Request payload: {payload}")
        response = requests.post(
            endpoint_url,
            headers=platform_api_headers(),
            data=payload,
        )

        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    _ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.text
        logger.debug(f"Response payload: {response_payload}")
        response_body = _RunResponseBody.model_validate_json(response_payload)

        # Confirm response contains response data for exactly one run request
        if (response_length := len(response_body.run_responses)) != 1:
            raise IndexError(
                "Exactly 1 run request expected to be associated with response "
                f"but found {response_length}"
            )

        # Check for any run configuration errors reported in the response and
        # raise exceptions as appropriate
        errors = response_body.run_responses[0].errors
        if errors is not None:
            for error in errors:
                raise RunConfigError(error.key, error.error)

    def _request_payload(self) -> _RunRequestPayload:
        return _RunRequestPayload(
            run_requests=[
                _RunRequest(
                    working_dir=str(Path.cwd()),
                    size=self.size,
                    fred_version=self.fred_version,
                    population=SynthPopModel(
                        version=self.params.synth_pop.name,
                        locations=self.params.synth_pop.locations,
                    ),
                    fred_args=(
                        _FREDArgsBuilder(self.fred_version)
                        .program(self.params.program)
                        .output_dir(self.output_dir.expanduser().resolve())
                        .overrides(self.params.model_params)
                        .seed(self.params.seed)
                        .start_date(self.params.start_date)
                        .end_date(self.params.end_date)
                        .locations(self.params.synth_pop.locations)
                        .build()
                    ),
                )
            ]
        )


class _FREDArgsBuilder:
    """Builder for list of arguments to pass to FRED via SRS.

    Handles correct argument naming for different FRED versions.

    Parameters
    ----------
    fred_version : str
        FRED version for the run.
    """

    def __init__(self, fred_version: str):
        self.fred_version = fred_version
        self._args: list[_FREDArg] = []

    def build(self) -> list[_FREDArg]:
        return self._args

    def program(self, program: Union[Path, str]) -> "_FREDArgsBuilder":
        self._args.append(_FREDArg(flag="-p", value=str(program)))
        return self

    def output_dir(self, output_dir: Path) -> "_FREDArgsBuilder":
        """Add the output directory argument to the FRED command line.

        Parameters
        ----------
        output_dir : Path
            Absolute path to the output directory.

        Returns
        -------
        _FREDArgsBuilder
            Current state of a partially built FRED command line.
        """
        if not output_dir.is_absolute():
            raise ValueError("output_dir must be an absolute path.")
        self._args.append(_FREDArg(flag="-d", value=str(output_dir)))
        return self

    def overrides(
        self, model_params: Optional[dict[str, Union[float, str]]]
    ) -> "_FREDArgsBuilder":
        if model_params is not None:
            self._args.extend(
                [_FREDArg(flag="-o", value=f"{k}={v}") for k, v in model_params.items()]
            )
        return self

    def seed(self, seed: int) -> "_FREDArgsBuilder":
        if fred_major_version(self.fred_version) < 11:
            # Use run number as an pseudo-seed
            self._args.append(_FREDArg(flag="-r", value=str(seed)))
        else:
            self._args.append(_FREDArg(flag="-s", value=str(seed)))
        return self

    def start_date(self, start_date: Optional[date]) -> "_FREDArgsBuilder":
        if start_date is not None:
            self._args.append(
                _FREDArg(
                    flag="--start-date",
                    value=start_date.strftime(r"%Y-%m-%d"),
                )
            )
        return self

    def end_date(self, end_date: Optional[date]) -> "_FREDArgsBuilder":
        if end_date is not None:
            self._args.append(
                _FREDArg(
                    flag="--end-date",
                    value=end_date.strftime(r"%Y-%m-%d"),
                )
            )
        return self

    def locations(self, locations: Optional[list[str]]) -> "_FREDArgsBuilder":
        if locations is not None and fred_major_version(self.fred_version) >= 11:
            # FRED 10 does not support --locations flag
            for location in locations:
                self._args.append(_FREDArg(flag="-l", value=location))
        return self


class UnauthorizedUserError(Exception):
    """Error indicating the user is not authorized to perform requested action.

    This can be thrown in the following circumstances:
        * User is not found in the Platform system
        * User does not have a subscription
        * User does not have sufficient compute credits

    Parameters
    ----------
    description : str
        Detailed description of the error as reported by SRS.

    Attributes
    ----------
    message : str
        Message describing the error.
    """

    def __init__(self, description: str):
        super().__init__(f"Authorization error: {description}")


class RunConfigError(Exception):
    """Error indicating there was a run configuration error.

    This is thrown when FRED Cloud API has reported an issue with the user's
    request.

    Parameters
    ----------
    key : str
        The general category of the error reported by FRED Cloud API, e.g.
        ``size`` for errors related to instance size, or ``fredVersion`` if the
        specified FRED version is not recognized.
    desc : str
        Detailed description of the error.

    Attributes
    ----------
    key : str
        The general category of the error reported by FRED Cloud API, e.g.
        ``size`` for errors related to instance size, or ``fredVersion`` if the
        specified FRED version is not recognized.
    desc : str
        Detailed description of the error.
    message : str
        Summary message describing the error.
    """

    def __init__(self, key: str, desc: str):
        self.key = key
        self.desc = desc
        super().__init__(f"{self.key} error: {self.desc}")
