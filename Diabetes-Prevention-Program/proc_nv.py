from pathlib import Path

from diabetes_prevention import Scenario, generate_summary_results_file

if __name__ == "__main__":
    generate_summary_results_file(
        Path("nv_results.csv"),
        [
            Scenario("without_program", "nv-db-no-program"),
            Scenario("with_program", "nv-db-with-program"),
        ],
        "32",
    )
