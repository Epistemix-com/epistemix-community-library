from pathlib import Path


def default_results_dir() -> Path:
    return Path.home() / "results"
