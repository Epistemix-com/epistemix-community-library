from itertools import product
from pathlib import Path
from typing import Iterable, NamedTuple

import pandas as pd
import geopandas as gpd

from epxexec.fred_job import FREDJob
from epxexec.epxresults.run import FREDRun


def get_state_block_groups_gdf(state_fips: str) -> gpd.GeoDataFrame:
    return gpd.read_file(_get_block_group_shp_url(state_fips)).pipe(
        _format_block_group_shp
    )


def _get_block_group_shp_url(state_fips: str) -> str:
    return (
        "https://www2.census.gov/geo/tiger/GENZ2022/shp/"
        f"cb_2022_{state_fips}_bg_500k.zip"
    )


def _format_block_group_shp(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Select, combine, and rename columns."""
    name_map = {"GEOID": "block_group", "NAME": "bg_num"}
    select_cols = [x for x in name_map.values()] + ["county_fips", "geometry"]
    return (
        gdf.assign(county_fips=lambda df: df["STATEFP"].str.cat(df["COUNTYFP"]))
        .rename(columns=name_map)
        .loc[:, select_cols]
    )


class VariableMeta(NamedTuple):
    varname: str
    filename: str


def get_results_df(
    job: FREDJob,
    variables: Iterable[VariableMeta],
    all_block_groups: pd.Series,
    year_range: tuple[int, int],
) -> pd.DataFrame:
    return (
        pd.concat(
            [
                (
                    _summarize_observation_csv(r, v.filename)
                    .pipe(_regularize_block_groups, all_block_groups, year_range)
                    .assign(variable=v.varname)
                    .assign(run_id=i)
                )
                for i, r in job.runs.items()
                for v in variables
            ]
        )
        .assign(calendar_year=lambda df: df["sim_year"] + year_range[0])
        .loc[:, ["run_id", "block_group", "calendar_year", "variable", "value"]]
        .reset_index(drop=True)
    )


def _summarize_observation_csv(run: FREDRun, csv_filename: str) -> pd.DataFrame:
    """For a given FRED run and csv output file, summarize the number of
    observations in the csv file by block group.

    Useful in situations where an agent writes a line to a file each
    under certain conditions in a model.
    """
    return (
        run.get_csv_output(csv_filename)
        .pipe(
            lambda df: (
                df.merge(
                    df["sim_day"]
                    .value_counts()
                    .sort_index()
                    .to_frame()
                    .reset_index()
                    .rename_axis("sim_year")
                    .reset_index()
                    .loc[:, ["sim_year", "sim_day"]],
                    on="sim_day",
                )
            )
        )
        # Exclude agents that don't have a census tract (agents living
        # in group quarters)
        .pipe(lambda df: df[df["block_group"] != 0])
        .assign(block_group=lambda df: df["block_group"].astype(str))
        .groupby(["sim_year", "block_group"])
        .size()
        .rename("value")
        .reset_index()
    )


def _regularize_block_groups(
    df: pd.DataFrame, all_block_groups: pd.Series, year_range: tuple[int, int]
):
    """Complete diabetes incidence dataframe such that block groups
    for which no incidence was observed in the simulation have 0
    reported, rather than a missing row.

    `year_range` is inclusive of both start and end year
    """
    sim_years = range(year_range[1] - year_range[0] + 1)
    return (
        pd.DataFrame.from_records(
            product(all_block_groups, sim_years),
            columns=["block_group", "sim_year"],
        )
        .merge(df, how="left", on=["block_group", "sim_year"])
        .fillna(0)
    )


class Scenario(NamedTuple):
    name: str
    job_key: str


def generate_summary_results_file(
    filename: Path,
    scenarios: Iterable[Scenario],
    state_fips: str,
    year_range: tuple[int, int],
):
    """Generate final results output file for a given state.

    Outputs are at the block group level and include the following variables:
    * n_diagnosed
    * cume_n_diagnosed
    """
    block_groups: pd.Series = get_state_block_groups_gdf(state_fips)["block_group"]
    df = (
        pd.concat([_get_scenario_data(s, block_groups, year_range) for s in scenarios])
        .pipe(lambda df: df[df["variable"] == "n_diagnosed"])
        .rename(
            columns={
                "value": "n_diagnosed",
                "cume_value": "cume_n_diagnosed",
            }
        )
        .loc[
            :,
            [
                "block_group",
                "calendar_year",
                "scenario",
                "n_diagnosed",
                "cume_n_diagnosed",
            ],
        ]
    )
    df.to_csv(filename, index=False)


def _get_scenario_data(
    scenario: Scenario, block_groups: pd.Series, year_range: tuple[int, int]
) -> FREDJob:
    job = FREDJob(job_key=scenario.job_key)
    variables = (VariableMeta("n_diagnosed", "diabetes_incidence.csv"),)
    return (
        get_results_df(job, variables, block_groups, year_range)
        .pipe(_average_over_runs)
        .assign(scenario=scenario.name)
    )


def _average_over_runs(df: pd.DataFrame) -> pd.DataFrame:
    index_cols = ["block_group", "calendar_year", "variable"]
    return (
        df.groupby(index_cols)["value"]
        .mean()
        .reset_index()
        .assign(value=lambda df: df["value"].round().astype(int))
        .groupby(["block_group", "variable"], as_index=False)
        # Recalculate cumulative over averaged values
        .apply(
            lambda df: (
                df.sort_values(by="calendar_year").assign(
                    cume_value=lambda df: df["value"].cumsum()
                )
            )
        )
    )
