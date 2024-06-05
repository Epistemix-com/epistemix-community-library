import pytest

from epx.run.fs import (
    FileFinderF11,
    FileFinderF10,
    FileFinderFactory,
    VarBySimDayPath,
)


def test_legacy_file_finder(sample_run_output_dir):
    success_output_dir = sample_run_output_dir("10.1.0") / "success"
    error_output_dir = sample_run_output_dir("10.1.0") / "error"

    success_ff = FileFinderF10(success_output_dir)
    assert success_ff.return_code == success_output_dir / "RUN1/return_code.txt"
    assert success_ff.errors is None
    assert success_ff.status == success_output_dir / "RUN1/status.txt"
    assert (
        success_ff.state("TRANS_CONDITION", "Excluded", "count")
        == success_output_dir / "RUN1/DAILY/TRANS_CONDITION.Excluded.txt"
    )
    assert (
        success_ff.state("TRANS_CONDITION", "Excluded", "new")
        == success_output_dir / "RUN1/DAILY/TRANS_CONDITION.newExcluded.txt"
    )
    assert (
        success_ff.state("TRANS_CONDITION", "Excluded", "cumulative")
        == success_output_dir / "RUN1/DAILY/TRANS_CONDITION.totExcluded.txt"
    )
    assert success_ff.dates == success_output_dir / "RUN1/DAILY/Date.txt"
    assert success_ff.epi_week == success_output_dir / "RUN1/DAILY/EpiWeek.txt"
    assert success_ff.pop_size == success_output_dir / "RUN1/DAILY/Popsize.txt"
    assert success_ff.conditions == success_output_dir / "RUN1/conditions.json"
    assert success_ff.return_code == success_output_dir / "RUN1/return_code.txt"
    assert success_ff.print_output == success_output_dir / "RUN1/fred_out.txt"
    assert (
        success_ff.csv_output("sample.csv")
        == success_output_dir / "RUN1/CSV/sample.csv"
    )
    assert (
        success_ff.text_output("sample_file.txt")
        == success_output_dir / "RUN1/CSV/sample_file.txt"
    )
    assert (
        success_ff.numeric("sample_numeric")
        == success_output_dir / "RUN1/DAILY/FRED.sample_numeric.txt"
    )
    assert (
        success_ff.list_table_end_of_sim("sample_list_table")
        == success_output_dir / "RUN1/LIST/sample_list_table.txt"
    )
    assert [x for x in success_ff.list_table_by_simday("sample_list_table")][
        0
    ] == VarBySimDayPath(0, success_output_dir / "RUN1/LIST/sample_list_table-0.txt")
    assert (
        success_ff.table_end_of_sim("sample_table")
        == success_output_dir / "RUN1/LIST/sample_table.txt"
    )
    assert [x for x in success_ff.table_by_simday("sample_table")][
        0
    ] == VarBySimDayPath(0, success_output_dir / "RUN1/LIST/sample_table-0.txt")
    assert (
        success_ff.list_end_of_sim("sample_list")
        == success_output_dir / "RUN1/LIST/sample_list.txt"
    )
    assert [x for x in success_ff.list_by_simday("sample_list")][0] == VarBySimDayPath(
        0, success_output_dir / "RUN1/LIST/sample_list-0.txt"
    )
    assert (
        success_ff.network("directed", 0) == success_output_dir / "RUN1/directed-0.vna"
    )

    error_ff = FileFinderF10(error_output_dir)
    assert error_ff.return_code == error_output_dir / "RUN1/return_code.txt"
    assert error_ff.errors == error_output_dir / "RUN1/errors.txt"
    assert error_ff.status == error_output_dir / "RUN1/status.txt"


def test_file_finder(sample_run_output_dir):
    success_output_dir = sample_run_output_dir("11.0.0") / "success"
    error_output_dir = sample_run_output_dir("11.0.0") / "error"

    success_ff = FileFinderF11(success_output_dir)
    assert success_ff.return_code == success_output_dir / "return_code.txt"
    assert success_ff.logs == success_output_dir / "logs.txt"
    assert (
        success_ff.state("TRANS_CONDITION", "Excluded", "count")
        == success_output_dir / "DAILY/TRANS_CONDITION.Excluded.txt"
    )
    assert (
        success_ff.state("TRANS_CONDITION", "Excluded", "new")
        == success_output_dir / "DAILY/TRANS_CONDITION.newExcluded.txt"
    )
    assert (
        success_ff.state("TRANS_CONDITION", "Excluded", "cumulative")
        == success_output_dir / "DAILY/TRANS_CONDITION.totExcluded.txt"
    )
    assert success_ff.dates == success_output_dir / "DAILY/Date.txt"
    assert success_ff.epi_week == success_output_dir / "DAILY/EpiWeek.txt"
    assert success_ff.pop_size == success_output_dir / "DAILY/Popsize.txt"
    assert success_ff.conditions == success_output_dir / "conditions.json"
    assert success_ff.return_code == success_output_dir / "return_code.txt"
    assert (
        success_ff.print_output == success_output_dir / "USER_OUTPUT/print_output.txt"
    )
    assert (
        success_ff.csv_output("sample.csv")
        == success_output_dir / "USER_OUTPUT/sample.csv"
    )
    assert (
        success_ff.text_output("sample_file.txt")
        == success_output_dir / "USER_OUTPUT/sample_file.txt"
    )
    assert (
        success_ff.numeric("sample_numeric")
        == success_output_dir / "VARIABLES/numeric.sample_numeric.csv"
    )
    assert [x for x in success_ff.list_table_by_simday("sample_list_table")][
        0
    ] == VarBySimDayPath(
        0, success_output_dir / "VARIABLES/list_table.sample_list_table-0.csv"
    )
    assert [x for x in success_ff.table_by_simday("sample_table")][
        0
    ] == VarBySimDayPath(0, success_output_dir / "VARIABLES/table.sample_table-0.csv")
    assert (
        success_ff.list_("sample_list")
        == success_output_dir / "VARIABLES/list.sample_list.csv"
    )
    assert (
        success_ff.network("directed", 0)
        == success_output_dir / "NETWORKS/directed-0.gv"
    )

    error_ff = FileFinderF11(error_output_dir)
    assert error_ff.return_code == error_output_dir / "return_code.txt"
    assert error_ff.logs == error_output_dir / "logs.txt"


def test_file_finder_factory(sample_run_output_dir, tmpdir):
    legacy_output_dir = sample_run_output_dir("10.1.0") / "success"
    output_dir = sample_run_output_dir("11.0.0") / "success"

    legacy_ff = FileFinderFactory(legacy_output_dir).build()
    assert isinstance(legacy_ff, FileFinderF10)

    legacy_ff_with_run_number = FileFinderFactory(legacy_output_dir, 1).build()
    assert isinstance(legacy_ff_with_run_number, FileFinderF10)
    assert legacy_ff_with_run_number.run_output_dir == legacy_output_dir / "RUN1"

    legacy_ff_with_run_number = FileFinderFactory(legacy_output_dir, 2).build()
    assert isinstance(legacy_ff_with_run_number, FileFinderF10)
    assert legacy_ff_with_run_number.run_output_dir == legacy_output_dir / "RUN2"
    with pytest.raises(FileNotFoundError):
        legacy_ff_with_run_number.dates

    ff = FileFinderFactory(output_dir).build()
    assert isinstance(ff, FileFinderF11)
