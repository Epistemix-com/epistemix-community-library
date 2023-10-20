from itertools import product

import pandas as pd
import numpy as np

import plotly
import plotly.express as px

MAPSTYLE="mapbox://styles/pnowell/cl4n9fic8001i15mnfmozrt8j"
TOKEN="pk.eyJ1IjoicG5vd2VsbCIsImEiOiJja201bHptMXkwZnQyMnZxcnFveTVhM2tyIn0.Pyarp9gHCON4reKvM2fZZg"


def get_states(job):
    states = pd.DataFrame()
    states['sim_date']=job.get_job_date_table().sim_date
    for x in ["Exposed", "InfectiousSymptomatic", "InfectiousAsymptomatic", "Recovered"]:
        counts = job.get_job_state_table(
            condition="RESP_DISEASE",
            state=x,
            count_type="new",)

        counts.rename(columns={'new':x},inplace=True)
        states = pd.merge(states, counts[x], left_index=True, right_index=True)

    states.rename(
        columns={'InfectiousAsymptomatic':'InfectiousA',
                 'InfectiousSymptomatic':'InfectiousS'},
        inplace=True)
    return states

def get_explocs(job):
    exp_data = job.runs[1].get_csv_output("exposure_locs.csv")
    exp_data['today'] = pd.to_datetime(exp_data['today'],format="%Y%m%d")
    exp_data["simday"] = (pd.to_datetime(exp_data.today) - pd.to_datetime("2022-01-01")).dt.days
    exp_data = exp_data.assign(ExposureLocation = exp_data.my_resp_exp_loc.map({-1:'InitialExposure', 0:'Other', 
                               1:'Household', 2:'BlockGroup', 3:'CensusTract',
                               4:'County', 5:'School', 6:'Workplace'},))
    return exp_data

def get_expmap_data(job):
    exp_data = get_explocs(job)
    exposure_locations = exp_data[exp_data.my_exp_lat!=0].groupby(["my_exp_lat", "my_exp_lon", "ExposureLocation"]).size().to_frame().reset_index().rename(columns={0:"NumberExposed"})
    exposure_locations = exposure_locations.assign(exp_scale=np.log10(exposure_locations.NumberExposed+0.5))
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
        df
        .pipe(_standardize_exposure_coords)
        .pipe(_add_dummy_exposure_locations)
    )


def _standardize_exposure_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Handle fact that for InitialExposure, BlockGroup, CensusTract, County,
    and Other, agent exposure locations are not well defined (fall back to
    (0, 0)) so we use agents' household location where available instead.
    """
    def choose_plot_coord(row: pd.Series, coord_type: str) -> float:
        default_col = f'my_exp_{coord_type}'
        fallback_col = f'{coord_type}_house'
        if row[default_col] != 0:
            return row[default_col]
        return row[fallback_col]

    return (
        df
        .rename(columns={'long_house': 'lon_house'})
        .assign(plot_lat=lambda df: df.apply(choose_plot_coord, coord_type='lat', axis=1))
        .assign(plot_lon=lambda df: df.apply(choose_plot_coord, coord_type='lon', axis=1))
    )


def _add_dummy_exposure_locations(df: pd.DataFrame) -> pd.DataFrame:
    """See https://github.com/plotly/plotly.js/issues/2861"""
    return pd.concat([
        df,
        pd.DataFrame.from_records(
        product(
                pd.date_range(df['today'].min(), df['today'].max()),
                df['ExposureLocation'].drop_duplicates()),
            columns=['today', 'ExposureLocation']
        )
    ])


def get_sim_exposures_by_demog_group(df: pd.DataFrame) -> pd.DataFrame:
    """Process `baseline_exposures` in preparation for plotting scatter
    plot colored by demographic group.
    
    Included demographic groups are specified in `_assign_demog_group`.
    """
    return (
        df
        .pipe(_standardize_exposure_coords)
        .pipe(_assign_demog_group)
        .pipe(_add_dummy_demog_group)
    )
    
    
def _assign_demog_group(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .assign(race_group=lambda df: (
            df['race'].apply(lambda x: 'White' if x == 1 else 'Minority ethnic')
        ))
        .assign(age_group=lambda df: (
            pd.cut(
                df['age'],
                bins=[0, 18, 65, 120],
                include_lowest=True,
                labels=['0-18', '19-65', '>65']
            )
        ))
        .assign(demog_group=lambda df: df['race_group'].str.cat(df['age_group'], sep=', '))
    )


def _add_dummy_demog_group(df: pd.DataFrame) -> pd.DataFrame:
    """See https://github.com/plotly/plotly.js/issues/2861"""
    return pd.concat([
        df,
        pd.DataFrame.from_records(
        product(
                pd.date_range(df['today'].min(), df['today'].max()),
                df['demog_group'].drop_duplicates()),
            columns=['today', 'demog_group']
        )
    ])


def plot_animation_by_exposure_location(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    category_orders = {
        'ExposureLocation': [
            'InitialExposure',
            'Household',
            'Workplace',
            'School',
            'BlockGroup',
            'CensusTract',
            'County',
            'Other',
        ]
    }
    fig = px.scatter_mapbox(
        get_sim_exposures_by_location(df),
        lat="plot_lat", 
        lon="plot_lon",     
        color="ExposureLocation",
        category_orders=category_orders,
        opacity=0.8,
        zoom=9.25, height=600,
        animation_frame='today'
    )

    fig.update_layout(mapbox_style=MAPSTYLE, mapbox_accesstoken=TOKEN)
    fig.update_layout(margin={"r":0,"t":60,"l":0,"b":0})
    fig.update_layout(title="Sites of Influenza Exposure",title_font_size=24,)
    return fig


def plot_animation_by_demog_group(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    category_orders = {
        'demog_group': [
            'White, 0-18',
            'White, 19-65',
            'White, >65',
            'Minority ethnic, 0-18',
            'Minority ethnic, 19-65',
            'Minority ethnic, >65',
        ]
    }

    fig = px.scatter_mapbox(
        get_sim_exposures_by_demog_group(df),
        lat="plot_lat",
        lon="plot_lon",
        color="demog_group",
        category_orders=category_orders,
        opacity=0.8,
        zoom=9.25, height=600,
        animation_frame='today'
    )

    fig.update_layout(mapbox_style=MAPSTYLE, mapbox_accesstoken=TOKEN)
    fig.update_layout(margin={"r":0,"t":60,"l":0,"b":0})
    fig.update_layout(title="Sites of Influenza Exposure",title_font_size=24)
    fig.update_layout(legend_title_text='Demographic group')
    return fig


def plot_time_series_by_demog_group(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    ts_df = (
        get_sim_exposures_by_demog_group(df)
        .groupby(['today', 'demog_group']).size()
        .swaplevel()
        # Ensure entries appear in the legend in the required order
        .loc[[
            'White, 0-18',
            'White, 19-65',
            'White, >65',
            'Minority ethnic, 0-18',
            'Minority ethnic, 19-65',
            'Minority ethnic, >65',
        ], :]
        .rename('n_exposures').to_frame().reset_index()
        .rename(columns={'today': 'date'})
    )
    
    fig = px.line(ts_df, x="date", y="n_exposures", color='demog_group')

    fig.update_layout(
        font_family="Epistemix Label",
        yaxis_title="New infections per day",
        xaxis_title="Date",
        legend_title="Demographic group",
        hovermode="x",height=450,
    )
    
    return fig
