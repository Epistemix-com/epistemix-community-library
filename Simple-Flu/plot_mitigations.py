from itertools import product

import pandas as pd
import numpy as np

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


def get_sim_exposures(df: pd.DataFrame) -> pd.DataFrame:
    """Process `baseline_exposures` in preparation for plotting.
    
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
