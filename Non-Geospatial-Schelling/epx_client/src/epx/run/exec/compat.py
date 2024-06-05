"""Functions for handling FRED 10 vs FRED 11 compatibility. """

import logging

import numpy as np

from epx.run.exec.common import RunParameters

logger = logging.getLogger(__name__)


def adapt_params_for_fred_version(
    params: RunParameters, fred_version: str
) -> RunParameters:
    """Adapt run parameters to be compatible with a specific FRED version.

    Parameters
    ----------
    params : RunParameters
        Run parameters to be adapted.
    fred_version : str
        FRED version to adapt the parameters for.

    Returns
    -------
    RunParameters
        Adapted run parameters.
    """
    if fred_major_version(fred_version) == 10:
        if params.seed is not None:
            seed = rescale_seed_to_run_number(params.seed)
            logger.info("Given seed rescaled to fit within FRED 10 run number range.")
        return RunParameters(
            program=params.program,
            synth_pop=params.synth_pop,
            start_date=params.start_date,
            end_date=params.end_date,
            model_params=params.model_params,
            seed=seed,
            compile_only=params.compile_only,
        )
    return params


def rescale_seed_to_run_number(seed: int) -> int:
    """Rescale seed to fit within the range of valid FRED run numbers.

    Parameters
    ----------
    seed : int
        Random seed on [0, 2**64) to be rescaled.

    Returns
    -------
    int
        Random run number on [1, max_run_number].

    Notes
    -----
    Depending on the platform it is compiled for, FRED stores the run number as
    either a 2 byte or 4 byte integer. Here we calculate the maximum allowed
    run number on the assumption that we can store a 2 byte integer.
    """
    max_run_number = 2 ** (8 * 2)
    rescaled_seed = np.interp(seed, [0, (2**64) - 1], [1, max_run_number])
    return int(rescaled_seed)


def fred_major_version(fred_version: str) -> int:
    """Extract the major version number from a FRED version string.

    Parameters
    ----------
    fred_version : str
        FRED version string.

    Returns
    -------
    int
        Major version number.
    """
    if fred_version == "latest":
        # TODO: Programmatically determine the latest version
        return 11
    return int(fred_version.split(".")[0])
