from datetime import date
import os
from pathlib import Path
from typing import Union
from unittest.mock import Mock, patch

import pytest

import pandas as pd

import pandera as pa

from epx.synthpop import SynthPop
from epx.run.run import Run, RunParameters
from epx.job.job import Job, ModelConfig, ModelConfigSweep
from epx.job.status import JobStatus
from epx.job.results import JobResults


@pytest.fixture
def sample_model_configs() -> list[ModelConfig]:
    return [
        ModelConfig(
            synth_pop=SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            model_params={"var1": 1.0, "var2": 10},
            seed=[12345, 23456],
            n_reps=2,
        ),
        ModelConfig(
            synth_pop=SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 29),
            model_params={"var1": 2.0, "var2": 20},
            seed=34567,
        ),
        ModelConfig(
            synth_pop=SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 29),
            model_params={"var1": 3.0, "var2": 30},
            n_reps=1,
        ),
        ModelConfig(
            synth_pop=SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 29),
            model_params={"var1": 4.0, "var2": 40},
            n_reps=2,
        ),
    ]


@pytest.fixture
def sample_results_dir(tmpdir) -> Path:
    return Path(tmpdir) / "results"


@pytest.fixture
def sample_cache_dir(tmpdir) -> Path:
    return Path(tmpdir) / "epx_client"


@pytest.fixture(scope="session")
def run_meta_schema():
    return pa.DataFrameSchema(
        {
            "run_id": pa.Column(int, checks=pa.Check.ge(0)),
            "program": pa.Column(str),
            "synth_pop": pa.Column(str),
            "locations": pa.Column(list[str], nullable=True),
            "start_date": pa.Column(pd.Timestamp, nullable=True),
            "end_date": pa.Column(pd.Timestamp, nullable=True),
            "params": pa.Column(dict[str, Union[float, str]], nullable=True),
            "seed": pa.Column(int, coerce=True),
            "size": pa.Column(str),
        },
        strict=True,
        ordered=True,
    )


def test_model_config():
    model_config = ModelConfig(
        synth_pop=SynthPop(
            "US_2010.v5", ["Jefferson_County_PA", "Allegheny_County_PA"]
        ),
        start_date=date(2024, 1, 1),
        end_date="2024-02-29",
        model_params={"var1": 1.0, "var2": 10},
        seed=12345,
    )
    assert model_config.synth_pop == SynthPop(
        "US_2010.v5", ["Jefferson_County_PA", "Allegheny_County_PA"]
    )
    assert model_config.start_date == date(2024, 1, 1)
    # Note that start and end dates are stored verbatim. Normalization to date
    # objects is done in the RunParameters class.
    assert model_config.end_date == "2024-02-29"
    assert model_config.model_params == {"var1": 1.0, "var2": 10}
    assert model_config.seed == 12345


def test_model_config_multi_rep():
    synth_pop = SynthPop("US_2010.v5", ["Jefferson_County_PA"])
    with pytest.raises(IndexError):
        # Two reps but only one seed
        ModelConfig(synth_pop=synth_pop, seed=12345, n_reps=2)

    with pytest.raises(IndexError):
        # Two reps but three seeds
        ModelConfig(synth_pop=synth_pop, seed=[12345, 23456, 34567], n_reps=2)

    model_config = ModelConfig(synth_pop=synth_pop, seed=None, n_reps=2)
    assert model_config.seed is None

    model_config = ModelConfig(synth_pop=synth_pop, seed=range(1, 3), n_reps=2)
    assert isinstance(model_config.seed, tuple)
    assert model_config.seed == (1, 2)


def test_model_config_single_rep():
    synth_pop = SynthPop("US_2010.v5", ["Jefferson_County_PA"])
    with pytest.raises(IndexError):
        # One rep but multiple seeds
        ModelConfig(synth_pop=synth_pop, seed=[12345, 23456], n_reps=1)

    model_config = ModelConfig(synth_pop=synth_pop, seed=[12345], n_reps=1)
    assert model_config.seed == 12345

    model_config = ModelConfig(synth_pop=synth_pop, seed=12345, n_reps=1)
    assert model_config.seed == 12345

    model_config = ModelConfig(synth_pop=synth_pop, seed=None, n_reps=1)
    assert model_config.seed is None


def test_model_config_sweep_repr():
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=[date(2024, 1, 1)],
        end_date=[date(2024, 1, 31), "2024-02-29"],
        model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
        seed=None,
    )
    assert repr(model_config_sweep) == (
        "ModelConfigSweep("
        "synth_pop=[SynthPop(name=US_2010.v5, locations=['Allegheny_County_PA']), "
        "SynthPop(name=US_2010.v5, locations=['Jefferson_County_PA'])], "
        "start_date=[datetime.date(2024, 1, 1)], "
        "end_date=[datetime.date(2024, 1, 31), '2024-02-29'], "
        "model_params=[{'var1': 1.0, 'var2': 10}, {'var1': 2.0, 'var2': 20}], "
        "seed=None, "
        "n_reps=1)"
    )


def test_model_config_sweep_explicit_seeds():
    # Single rep per config
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=[date(2024, 1, 1)],
        end_date=[date(2024, 1, 31), "2024-02-29"],
        model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
        seed=range(12345, 12345 + 8),
        n_reps=1,
    )

    model_configs = [x for x in model_config_sweep]
    assert len(model_configs) == 8
    for mc in model_configs:
        assert isinstance(mc, ModelConfig)
        assert isinstance(mc.seed, int)

    # Multiple reps per config
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=[date(2024, 1, 1)],
        end_date=[date(2024, 1, 31), "2024-02-29"],
        model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
        seed=range(12345, 12345 + 16),
        n_reps=2,
    )

    model_configs = [x for x in model_config_sweep]
    assert len(model_configs) == 8
    for mc in model_configs:
        assert isinstance(mc, ModelConfig)
        assert isinstance(mc.seed, tuple)

    with pytest.raises(IndexError):
        # Incorrect number of seeds specified
        ModelConfigSweep(
            synth_pop=[
                SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
                SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
            ],
            start_date=[date(2024, 1, 1)],
            end_date=[date(2024, 1, 31), "2024-02-29"],
            model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
            seed=[12345, 54321],
        )


def test_model_config_sweep_explicit_single_seed():
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=[date(2024, 1, 1)],
        end_date=[date(2024, 1, 31), "2024-02-29"],
        model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
        seed=12345,
    )

    model_configs = [x for x in model_config_sweep]
    assert len(model_configs) == 8
    for mc in model_configs:
        assert isinstance(mc, ModelConfig)
        assert isinstance(mc.seed, int)


def test_model_config_sweep_none_seed():
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=[date(2024, 1, 1)],
        end_date=[date(2024, 1, 31), "2024-02-29"],
        model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
        seed=None,
    )

    model_configs = [x for x in model_config_sweep]
    assert len(model_configs) == 8
    for mc in model_configs:
        assert isinstance(mc, ModelConfig)
        assert isinstance(mc.seed, int)


def test_model_config_sweep_none_model_params():
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=[date(2024, 1, 1)],
        end_date=[date(2024, 1, 31), "2024-02-29"],
        model_params=None,
        seed=None,
    )

    model_configs = [x for x in model_config_sweep]
    assert len(model_configs) == 4
    for mc in model_configs:
        assert isinstance(mc, ModelConfig)
        assert isinstance(mc.seed, int)


def test_model_config_sweep_none_start_date():
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=None,
        end_date=[date(2024, 1, 31), "2024-02-29"],
        model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
        seed=None,
    )

    model_configs = [x for x in model_config_sweep]
    assert len(model_configs) == 8
    for mc in model_configs:
        assert isinstance(mc, ModelConfig)
        assert mc.start_date is None


def test_model_config_sweep_none_end_date():
    model_config_sweep = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        ],
        start_date=["2024-01-01"],
        end_date=None,
        model_params=[{"var1": 1.0, "var2": 10}, {"var1": 2.0, "var2": 20}],
        seed=None,
    )

    model_configs = [x for x in model_config_sweep]
    assert len(model_configs) == 4
    for mc in model_configs:
        assert isinstance(mc, ModelConfig)
        assert mc.end_date is None


@patch("epx.run.exec.common.random_seed", side_effect=[45678, 56789, 67890])
def test_job_init(_, sample_model_configs, sample_results_dir, sample_cache_dir):
    with patch.dict(os.environ, {"EPX_CACHE_DIR": str(sample_cache_dir)}):
        job = Job(
            program="main.fred",
            config=sample_model_configs,
            key="test",
            results_dir=sample_results_dir,
        )
        expected_run_parameters = [
            RunParameters(
                program="main.fred",
                synth_pop=SynthPop(
                    name="US_2010.v5", locations=["Jefferson_County_PA"]
                ),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                model_params={"var1": 1.0, "var2": 10},
                seed=12345,
                compile_only=False,
            ),
            RunParameters(
                program="main.fred",
                synth_pop=SynthPop(
                    name="US_2010.v5", locations=["Jefferson_County_PA"]
                ),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                model_params={"var1": 1.0, "var2": 10},
                seed=23456,
                compile_only=False,
            ),
            RunParameters(
                program="main.fred",
                synth_pop=SynthPop(
                    name="US_2010.v5", locations=["Jefferson_County_PA"]
                ),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 2, 29),
                model_params={"var1": 2.0, "var2": 20},
                seed=34567,
                compile_only=False,
            ),
            RunParameters(
                program="main.fred",
                synth_pop=SynthPop(
                    name="US_2010.v5", locations=["Jefferson_County_PA"]
                ),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 2, 29),
                model_params={"var1": 3.0, "var2": 30},
                seed=45678,
                compile_only=False,
            ),
            RunParameters(
                program="main.fred",
                synth_pop=SynthPop(
                    name="US_2010.v5", locations=["Jefferson_County_PA"]
                ),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 2, 29),
                model_params={"var1": 4.0, "var2": 40},
                seed=56789,
                compile_only=False,
            ),
            RunParameters(
                program="main.fred",
                synth_pop=SynthPop(
                    name="US_2010.v5", locations=["Jefferson_County_PA"]
                ),
                start_date=date(2024, 1, 1),
                end_date=date(2024, 2, 29),
                model_params={"var1": 4.0, "var2": 40},
                seed=67890,
                compile_only=False,
            ),
        ]

        assert [x.params for x in job._runs] == expected_run_parameters
        assert [x.output_dir for x in job._runs] == [
            sample_results_dir / f"test/{i}" for i in range(6)
        ]


def test_job_from_key(sample_model_configs, sample_results_dir, sample_cache_dir):
    with patch.dict(os.environ, {"EPX_CACHE_DIR": str(sample_cache_dir)}):
        job = Job(
            program="main.fred",
            config=sample_model_configs,
            key="test",
            results_dir=sample_results_dir,
        )
        job._init_cache()
        job._write_job_config()
        job_from_key = Job.from_key("test")
        assert (sample_cache_dir / "jobs/test/job.json").exists()
        assert job == job_from_key


def test_job_execute(sample_model_configs, sample_results_dir, sample_cache_dir):
    with patch.dict(os.environ, {"EPX_CACHE_DIR": str(sample_cache_dir)}):
        job = Job(
            program="main.fred",
            config=sample_model_configs,
            key="test",
            results_dir=sample_results_dir,
        )
        mocked_runs = [Mock(spec=Run), Mock(spec=Run)]
        job._runs = mocked_runs
        job.execute()
        assert (sample_cache_dir / "jobs/test/job.json").exists()
        for run in mocked_runs:
            run.execute.assert_called_once()


def test_job_run_meta(
    sample_model_configs, sample_results_dir, sample_cache_dir, run_meta_schema
):
    with patch.dict(os.environ, {"EPX_CACHE_DIR": str(sample_cache_dir)}):
        model_configs = (
            *sample_model_configs,
            ModelConfig(
                synth_pop=SynthPop(
                    "US_2010.v5", ["Jefferson_County_PA", "Allegheny_County_PA"]
                ),
                start_date=None,
                end_date=None,
                model_params=None,
                seed=12345,
            ),
        )
        job = Job(
            program="main.fred",
            config=model_configs,
            key="test",
            results_dir=sample_results_dir,
        )
        run_meta = job.run_meta
        assert len(run_meta.index) == 7
        run_meta_schema.validate(run_meta)


def test_job_status(sample_model_configs, sample_results_dir, sample_cache_dir):
    with patch.dict(os.environ, {"EPX_CACHE_DIR": str(sample_cache_dir)}):
        job = Job(
            program="main.fred",
            config=sample_model_configs,
            key="test",
            results_dir=sample_results_dir,
        )
        assert isinstance(job.status, JobStatus)
        assert job.status.name == "NOT STARTED"


def test_job_results(sample_model_configs, sample_results_dir, sample_cache_dir):
    with patch.dict(os.environ, {"EPX_CACHE_DIR": str(sample_cache_dir)}):
        job = Job(
            program="main.fred",
            config=sample_model_configs,
            key="test",
            results_dir=sample_results_dir,
        )
        assert isinstance(job.results, JobResults)
