from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture(scope="session")
def sample_run_output_dir() -> Callable[[str], Path]:
    def _sample_run_output_dir(fred_version: str) -> Path:
        p = Path(__file__).parents[1] / (
            f"resources/tests/sample-run-outputs/FRED-{fred_version.replace('.', '-')}"
        )
        if not p.is_dir():
            raise FileNotFoundError(p)
        return p

    return _sample_run_output_dir


@pytest.fixture
def sample_empty_output_dir(tmpdir) -> Path:
    """Temporary directory to use for sample results output."""
    return Path(tmpdir.mkdir("results"))
