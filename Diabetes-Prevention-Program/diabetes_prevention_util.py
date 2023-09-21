from itertools import product

import pandas as pd
import geopandas as gpd

import plotly.express as px
from plotly.graph_objs import Figure

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


def process_diabetes_incidence_output(
    job: FREDJob, all_block_groups: pd.Series, earliest_year: int
) -> pd.DataFrame:
    """Generate post-processed table using FRED csv output file
    'diabetes_incidence.csv'.
    """

    def process_single_run(run: FREDRun, run_id: int) -> pd.DataFrame:
        return (
            job.runs[run_id]
            .get_csv_output("diabetes_incidence.csv")
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
            .assign(calendar_year=lambda df: df["sim_year"] + earliest_year)
            .assign(block_group=lambda df: df["block_group"].astype(str))
            # Exclude agents that don't have a census tract (agents living
            # in group quarters)
            .pipe(lambda df: df[df["block_group"] != 0])
            .groupby(["calendar_year", "block_group"])
            .size()
            .rename("n_diagnosed")
            .reset_index()
            .pipe(_regularize_block_groups, all_block_groups)
            .groupby("block_group", as_index=False)
            .apply(
                lambda df: (
                    df.sort_values(by="calendar_year").assign(
                        cume_n_diagnosed=lambda df: df["n_diagnosed"].cumsum()
                    )
                )
            )
            .reset_index(drop=True)
            .assign(run_id=run_id)
        )

    return pd.concat([process_single_run(run, i + 1) for i, run in enumerate(job.runs)])


def _regularize_block_groups(df: pd.DataFrame, all_block_groups: pd.Series):
    """Complete diabetes incidence dataframe such that block groups
    for which no incidence was observed in the simulation have 0
    reported, rather than a missing row.
    """
    earliest_year = df["calendar_year"].min()
    latest_year = df["calendar_year"].max()
    return (
        pd.DataFrame.from_records(
            product(all_block_groups, range(earliest_year, latest_year + 1)),
            columns=["block_group", "calendar_year"],
        )
        .merge(df, how="left", on=["block_group", "calendar_year"])
        .fillna(0)
        .assign(n_diagnosed=lambda df: df["n_diagnosed"].astype(int))
    )


def plot_cume_diagnoses(
    incidence_df: pd.DataFrame, block_group_gdf: gpd.GeoDataFrame, location_name: str
) -> Figure:
    earliest_year = incidence_df["calendar_year"].min()
    return px.choropleth(
        data_frame=incidence_df,
        geojson=block_group_gdf,
        featureidkey="properties.block_group",
        locations="block_group",
        color="cume_n_diagnosed",
        animation_frame="calendar_year",
        fitbounds="geojson",
        range_color=_get_value_range(incidence_df, "cume_n_diagnosed"),
        width=700,
        height=500,
        labels={
            "cume_n_diagnosed": r"Cumulative<br>diagnoses",
            "calendar_year": "Year",
        },
        title=f"Diabetes diagnoses in {location_name} since {earliest_year}",
    )


def _get_value_range(df: pd.DataFrame, var_name: str) -> tuple[int, int]:
    def round_to_nearest_n(x, n=10):
        return int(n * round(float(x) / n))

    return (
        round_to_nearest_n(df[var_name].min()),
        round_to_nearest_n(df[var_name].max()),
    )
