from epx.synthpop import SynthPop
from epx.run.exec.common import RunParameters
from epx.run.exec.compat import (
    adapt_params_for_fred_version,
    rescale_seed_to_run_number,
)


def test_rescale_seed_to_run_number():
    assert isinstance(rescale_seed_to_run_number(10), int)
    assert rescale_seed_to_run_number(0) == 1
    assert rescale_seed_to_run_number(2**64 - 1) == 65536  # 2**16 = 65536


def test_adapt_params_for_fred_version():
    params = RunParameters(
        program="main.fred",
        synth_pop=SynthPop("US_2010.v5", ["Location1", "Location2"]),
        start_date="2021-01-01",
        end_date="2021-01-02",
        seed=0,
    )

    # Unchanged if FRED 11
    assert adapt_params_for_fred_version(params, "11.0.0") == params
    assert adapt_params_for_fred_version(params, "10.1.1") == RunParameters(
        program="main.fred",
        synth_pop=SynthPop("US_2010.v5", ["Location1", "Location2"]),
        start_date="2021-01-01",
        end_date="2021-01-02",
        seed=1,  # Rescaled from 0
    )
