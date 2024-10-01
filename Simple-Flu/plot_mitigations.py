from itertools import product

import pandas as pd
import numpy as np

import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import requests

# Use the Epistemix default plotly template
r = requests.get("https://gist.githubusercontent.com/daniel-epistemix/8009ad31ebfa96ac97b7be038c014c0d/raw/320c3b0ca3dfbf7946e49c97254fa65d4753aeac/epx_plotly_theme.json")
if r.status_code == 200:
    pio.templates["epistemix"] = go.layout.Template(r.json())
    pio.templates.default = "epistemix"

MAPSTYLE = "mapbox://styles/epxadmin/cm0ve9m13000501nq8q1zdf5p"
TOKEN = "pk.eyJ1IjoiZXB4YWRtaW4iLCJhIjoiY20wcmV1azZ6MDhvcTJwcTY2YXpscWsxMSJ9._ROunfMS6hgVh1LPQZ4NGg"


def get_states(job):
    states = pd.DataFrame()
    states["sim_date"] = job.results.dates().sim_date
    for x in [
        "Exposed",
        "InfectiousSymptomatic",
        "InfectiousAsymptomatic",
        "Recovered",
    ]:
        counts = job.results.state(
            "RESP_DISEASE",
            x,
            "new",
        )

        counts.rename(columns={"new": x}, inplace=True)
        states = pd.merge(states, counts[x], left_index=True, right_index=True)

    states.rename(
        columns={
            "InfectiousAsymptomatic": "InfectiousA",
            "InfectiousSymptomatic": "InfectiousS",
        },
        inplace=True,
    )
    return states


def get_explocs(job):
    exp_data = job.results.csv_output("exposure_locs.csv")
    exp_data["today"] = (
        pd.to_datetime(exp_data["today"], format="%Y%m%d")
    ).dt.date.apply(pd.Timestamp)
    exp_data["simday"] = (
        pd.to_datetime(exp_data.today) - pd.to_datetime("2023-01-01")
    ).dt.days
    exp_data = exp_data.assign(
        ExposureLocation=exp_data.my_resp_exp_loc.map(
            {
                -1: "InitialExposure",
                0: "Other",
                1: "Household",
                2: "BlockGroup",
                3: "CensusTract",
                4: "County",
                5: "School",
                6: "Workplace",
            },
        )
    )
    return exp_data


def get_expmap_data(job):
    exp_data = get_explocs(job)
    exposure_locations = (
        exp_data[exp_data.my_exp_lat != 0]
        .groupby(["my_exp_lat", "my_exp_lon", "ExposureLocation"])
        .size()
        .to_frame()
        .reset_index()
        .rename(columns={0: "NumberExposed"})
    )
    exposure_locations = exposure_locations.assign(
        exp_scale=np.log10(exposure_locations.NumberExposed + 0.5)
    )
    return exposure_locations


def get_sim_exposures_by_location(df: pd.DataFrame) -> pd.DataFrame:
    """Process `baseline_exposures` in preparation for plotting scatter
    plot colored by exposure location type (Household, Workplace, etc).

    To make an animated plot of exposures we need to make some tweaks to the
    raw `baseline_exposures` DataFrame:

    1. Account for the fact that the model doesn't output correct
       latitude/ longitude values for agents exposed outside of
       Household, Workplace, or School. This is achieved by using
       the agents' household location as a proxy for their exposure
       location
    2. Add 'dummy' exposures so that every date in the simulation
       has the full set of exposure locations represented in its
       legend. This is a workaround for the Plotly issue described
       here https://github.com/plotly/plotly.js/issues/2861
    """
    return (
        df.pipe(_standardize_exposure_coords)
        .pipe(_add_dummy_exposure_locations)
    )


def _standardize_exposure_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Handle fact that for InitialExposure, BlockGroup, CensusTract, County,
    and Other, agent exposure locations are not well defined (fall back to
    (0, 0)) so we use agents' household location where available instead.
    """

    def choose_plot_coord(row: pd.Series, coord_type: str) -> float:
        default_col = f"my_exp_{coord_type}"
        fallback_col = f"{coord_type}_house"
        if row[default_col] != 0:
            return row[default_col]
        return row[fallback_col]

    return (
        df.rename(columns={"long_house": "lon_house"})
        .assign(
            plot_lat=lambda df: df.apply(choose_plot_coord, coord_type="lat", axis=1)
        )
        .assign(
            plot_lon=lambda df: df.apply(choose_plot_coord, coord_type="lon", axis=1)
        )
    )


def _add_dummy_exposure_locations(df: pd.DataFrame) -> pd.DataFrame:
    """See https://github.com/plotly/plotly.js/issues/2861"""
    return pd.concat(
        [
            df,
            pd.DataFrame.from_records(
                product(
                    pd.date_range(df["today"].min(), df["today"].max()),
                    df["ExposureLocation"].drop_duplicates(),
                ),
                columns=["today", "ExposureLocation"],
            ),
        ]
    )


def get_sim_exposures_by_demog_group(df: pd.DataFrame) -> pd.DataFrame:
    """Process `baseline_exposures` in preparation for plotting scatter
    plot colored by demographic group.

    Included demographic groups are specified in `_assign_demog_group`.
    """
    
    return (
        df.pipe(_standardize_exposure_coords)
        .pipe(_assign_demog_group)
        .pipe(_add_dummy_demog_group)
        .sort_values(by="today")
    )


def _assign_demog_group(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(
            race_group=lambda df: (
                df["race"].apply(lambda x: "White" if x == 1 else "Minority ethnic")
            )
        )
        .assign(
            age_group=lambda df: (
                pd.cut(
                    df["age"],
                    bins=[0, 18, 65, 120],
                    include_lowest=True,
                    labels=["0-18", "19-65", ">65"],
                )
            )
        )
        .assign(
            demog_group=lambda df: df["race_group"].str.cat(df["age_group"], sep=", ")
        )
    )


def _add_dummy_demog_group(df: pd.DataFrame) -> pd.DataFrame:
    """See https://github.com/plotly/plotly.js/issues/2861"""
    return pd.concat(
        [
            df,
            pd.DataFrame.from_records(
                product(
                    pd.date_range(df["today"].min(), df["today"].max()),
                    df["demog_group"].drop_duplicates(),
                ),
                columns=["today", "demog_group"],
            ),
        ]
    )


def plot_animation_by_exposure_location(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    category_orders = {
        "ExposureLocation": [
            "InitialExposure",
            "Household",
            "Workplace",
            "School",
            "BlockGroup",
            "CensusTract",
            "County",
            "Other",
        ]
    }
    sim_exposures = get_sim_exposures_by_location(df).sort_values(by="today")
    sim_exposures.today = pd.to_datetime(sim_exposures.today).dt.date
    fig = px.scatter_mapbox(
        sim_exposures,
        lat="plot_lat",
        lon="plot_lon",
        color="ExposureLocation",
        category_orders=category_orders,
        opacity=0.8,
        zoom=9.25,
        height=600,
        animation_frame="today",
    )

    fig.update_layout(mapbox_style=MAPSTYLE, mapbox_accesstoken=TOKEN)
    fig.update_layout(margin={"r": 0, "t": 60, "l": 0, "b": 0})
    fig.update_layout(title="Sites of Influenza Exposure", title_font_size=24)
    fig.update_layout(legend_title_text="Exposure location type")
    return fig


def plot_animation_by_demog_group(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    category_orders = {
        "demog_group": [
            "White, 0-18",
            "White, 19-65",
            "White, >65",
            "Minority ethnic, 0-18",
            "Minority ethnic, 19-65",
            "Minority ethnic, >65",
        ]
    }

    sim_exposures = get_sim_exposures_by_demog_group(df).sort_values(by="today")
    sim_exposures.today = pd.to_datetime(sim_exposures.today).dt.date
    fig = px.scatter_mapbox(
        sim_exposures,
        lat="plot_lat",
        lon="plot_lon",
        color="demog_group",
        category_orders=category_orders,
        opacity=0.8,
        zoom=9.25,
        height=600,
        animation_frame="today",
    )

    fig.update_layout(mapbox_style=MAPSTYLE, mapbox_accesstoken=TOKEN)
    fig.update_layout(margin={"r": 0, "t": 60, "l": 0, "b": 0})
    fig.update_layout(title="Sites of Influenza Exposure", title_font_size=24)
    fig.update_layout(legend_title_text="Demographic group")
    return fig


def plot_time_series_by_demog_group(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    ts_df = (
        get_sim_exposures_by_demog_group(df)
        .groupby(["today", "demog_group"])
        .size()
        .swaplevel()
        # Ensure entries appear in the legend in the required order
        .loc[
            [
                "White, 0-18",
                "White, 19-65",
                "White, >65",
                "Minority ethnic, 0-18",
                "Minority ethnic, 19-65",
                "Minority ethnic, >65",
            ],
            :,
        ]
        .rename("n_exposures")
        .to_frame()
        .reset_index()
        .rename(columns={"today": "date"})
    )

    fig = px.line(ts_df, x="date", y="n_exposures", color="demog_group")

    fig.update_layout(
        font_family="Epistemix Label",
        yaxis_title="New infections per day",
        xaxis_title="Date",
        legend_title="Demographic group",
        hovermode="x",
        height=450,
    )

    return fig

def plot_scenario_ecdf(jobs = [], scenarios = [], scenario_name = ""):
    
    job_dfs = []
    job_peak_dates = []
    job_peak_y = []
    job_peak_vals = []
    for job, scenario in zip(jobs, scenarios):
        job_df = get_states(job)[["sim_date", "Exposed"]]
        idxmax = job_df["Exposed"].idxmax()
        max_row = job_df.loc[idxmax]
        df_to_max_row = job_df.loc[list(range(idxmax))]
        job_peak_dates.append(max_row["sim_date"])
        job_peak_vals.append(max_row["Exposed"])
        job_peak_y.append(df_to_max_row["Exposed"].sum())
        job_df["Scenario"] = scenario
        job_dfs.append(job_df)
        
    df = pd.concat(job_dfs)
    fig = px.ecdf(df, x="sim_date", y="Exposed", color="Scenario", ecdfnorm=None)
    
    fig.add_trace(go.Scatter(
        x=job_peak_dates,
        y=job_peak_y,
        mode="markers+text",
        text=[f"{peak}" for peak in job_peak_vals],
        textposition="top center",
        name="Size of Peak"
    ))

    fig.update_layout(
        font_family="Epistemix Label",
        yaxis_title="Cumulative Infections",
        xaxis_title="Date",
        title=f"Scenario Exploration: {scenario_name}",
        title_font_size=24,
        xaxis_range=["2023-01-01","2023-06-30"],
        hovermode="x",height=450,
    )
    
    return fig