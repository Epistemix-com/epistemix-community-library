import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from epx import Job

# Import Epistemix plotly template for visualization
import requests

# Use the Epistemix default plotly template
r = requests.get("https://gist.githubusercontent.com/daniel-epistemix/8009ad31ebfa96ac97b7be038c014c0d/raw/320c3b0ca3dfbf7946e49c97254fa65d4753aeac/epx_plotly_theme.json")
if r.status_code == 200:
    pio.templates['epistemix'] = go.layout.Template(r.json())
    pio.templates.default = 'epistemix'

def get_outcomes(job, run=0):
    data = (
        job.results.csv_output('outcomes.csv')
            .pipe(lambda df: df.loc[df['run_id'] == run])
            .drop(columns = ['run_id'])
            .groupby(['id', 'year'])
            .first()
    )
    return data

def sample_households_outcomes(job, run=0, random_state=109316):
    households = (
        job.results.csv_output('household.csv')
            .pipe(lambda df: df.loc[df['run_id'] == run])
            .drop(columns = ['run_id'])
            .groupby(['lat', 'long'])
            .sample(1)
            .set_index('id')
    )
    outcomes = get_outcomes(job).reset_index().set_index('id')
    
    outcomes = households.join(outcomes, how='inner')
    
    cols = outcomes.columns.tolist()
    cols.append('color')
    
    outcomes['_exposed']    = outcomes['exposed']
    outcomes['_vaccinated'] = 2*outcomes['vaccinated']
    outcomes['_immunized']  = 3*outcomes['immunized']
    
    outcomes['color'] = outcomes[['_exposed', '_vaccinated', '_immunized']].max(axis=1).astype(str)
    outcomes['color'] = outcomes['color'].replace(
        {
            '0': 'None',
            '1': 'Infected',
            '2': 'Vaccinated',
            '3': 'Immune'
        }
    )
    
    outcomes = outcomes[cols].reset_index()       
    outcomes = outcomes.loc[outcomes['year'] > outcomes['year'].min()]
    
    dummy_entries = pd.DataFrame(
                        [[0, 0, 0, outcomes['year'].min(), 0, 0, 0, 'None'],
                         [0, 0, 0, outcomes['year'].min(), 0, 0, 0, 'Infected'], 
                         [0, 0, 0, outcomes['year'].min(), 0, 0, 0, 'Vaccinated'],
                         [0, 0, 0, outcomes['year'].min(), 0, 0, 0, 'Immune']], 
                    columns=['id'] + cols)
    outcomes = pd.concat([outcomes, dummy_entries])

    return households, outcomes
    
def get_states(job, run=0):
    states = pd.DataFrame()
    states['sim_date'] = (
        job.results.dates()
            .pipe(lambda df: df.loc[df['run_id'] == run])['sim_date']
    )
    for x in ['Exposed', 'Infectious', 'Recovered']:
        counts = (
            job.results.state(
                condition='INFLUENZA',
                state=x,
                count_type='new'
            ).pipe(lambda df: df.loc[df['run_id'] == run])
        )

        counts.rename(columns={'new':x},inplace=True)
        states = pd.merge(states, counts[x], left_index=True, right_index=True)

    return states

def get_epi_curves(job):
    
    baseline_states = get_states(job)
    
    fig = go.Figure()

    for x in ['Exposed', 'Infectious', 'Recovered']:
        fig.add_trace(
            go.Scatter(
                x=baseline_states['sim_date'],
                y=baseline_states[x],
                mode='lines',
                line=go.scatter.Line(width=3),
                showlegend=True,
                name=x)
        )

    fig.update_layout(
        font_family='Epistemix Label',
        yaxis_title='New infections per day',
        xaxis_title='Date',
        legend_title='State',
        title='The Spread of Influenza in Kewaunee County, WI',
        title_font_size=24,
        xaxis_range=['2022-01-01','2031-12-31'],
        # xaxis_range=['2022-01-01','2041-12-31'],
        hovermode='x',height=450,
    )
    
    return fig

def get_household_animation(job, run=0):
    households, outcomes = sample_households_outcomes(job, run)
    
    netlogo = {
            # 'link'         : 'rgb(114, 114, 114)', # gray 4
            'None'       : 'rgb(252, 225, 208)', # peach 29: neither
            'Infected'   : 'rgb(215,  50,  41)', # red 15: exposed, not vaccinated
            'Vaccinated' : 'rgb( 52,  93, 169)', # blue 105: vaccinated, not immune
            'Immune'     : 'rgb( 31,  57, 104)', # blue 103: immunized
          }

    # epistemix = {} # TODO: Setup Epistemix colors

    # calculate lat, long to pass to mapbox for map center
    lat_cen = outcomes['lat'].median()
    long_cen = outcomes['long'].median()

    # set up Epistemix house map tiles
    mapstyle="mapbox://styles/epxadmin/cm0ve9m13000501nq8q1zdf5p"
    token="pk.eyJ1IjoiZXB4YWRtaW4iLCJhIjoiY20wcmV1azZ6MDhvcTJwcTY2YXpscWsxMSJ9._ROunfMS6hgVh1LPQZ4NGg"

    # create the figure
    fig = px.scatter_mapbox(
        outcomes, 
        lat='lat',
        lon='long',
        color='color',
        # category_orders = {'color': list(netlogo.keys())},
        # color_discrete_sequence = list(netlogo.values()),
        color_discrete_map = netlogo, # change color palette here
        animation_frame='year', 
        animation_group='id',
        height=700, 
        zoom=11,
        labels={'color':'Status'}
    )

    fig.update_layout(mapbox_style=mapstyle, mapbox_accesstoken=token)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(margin={'r':20,'t':10,'l':10,'b':3})
    
    return fig