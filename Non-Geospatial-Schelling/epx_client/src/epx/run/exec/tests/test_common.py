from datetime import date
from pathlib import Path

from epx.synthpop import SynthPop
from epx.run.exec.common import RunParameters


def test_run_parameters():
    params = RunParameters(
        "main.fred",
        SynthPop("US_2010.v5", ["Location1", "Location2"]),
        date(2024, 1, 1),
        "2024-02-29",
        model_params={"var1": 10, "var2": 11.1},
        seed=42,
        compile_only=True,
    )
    assert params.program == Path("main.fred")
    assert params.synth_pop == SynthPop("US_2010.v5", ["Location1", "Location2"])
    assert params.start_date == date(2024, 1, 1)
    assert params.end_date == date(2024, 2, 29)
    assert params.model_params == {"var1": 10, "var2": 11.1}
    assert params.seed == 42
    assert params.compile_only is True

    # Confirm that random seed is generated if not specified
    params = RunParameters(
        "main.fred",
        SynthPop("US_2010.v5", ["Location1", "Location2"]),
        date(2024, 1, 1),
        "2024-02-29",
    )
    assert isinstance(params.seed, int)


def test_run_parameters_repr():
    params = RunParameters(
        "main.fred",
        SynthPop("US_2010.v5", ["Location1", "Location2"]),
        date(2024, 1, 1),
        "2024-02-29",
        model_params={"var1": 10, "var2": 11.1},
        seed=42,
        compile_only=True,
    )
    assert (
        repr(params) == "RunParameters("
        "program=main.fred, "
        "synth_pop=SynthPop(name=US_2010.v5, locations=['Location1', 'Location2']), "
        "start_date=2024-01-01, "
        "end_date=2024-02-29, "
        "model_params={'var1': 10, 'var2': 11.1}, "
        "seed=42, "
        "compile_only=True)"
    )
