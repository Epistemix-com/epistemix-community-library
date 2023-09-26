import pandas as pd
import geopandas as gpd

import plotly.express as px
from plotly.graph_objs import Figure
import plotly.io as pio

from epxexec.visual.utils import default_plotly_template

pio.templates["epistemix"] = default_plotly_template()
pio.templates.default = "epistemix"


DEFAULT_MAPSTYLE = "mapbox://styles/pnowell/cl4n9fic8001i15mnfmozrt8j"
DEFAULT_MAPBOX_TOKEN = (
    "pk.eyJ1IjoicG5vd2VsbCIsImEiOiJja201bHptMXkwZnQyMnZxcnFveTVhM2tyIn0."
    "Pyarp9gHCON4reKvM2fZZg"
)


class MapboxConfig:
    def __init__(
        self, mapstyle: str = DEFAULT_MAPSTYLE, token: str = DEFAULT_MAPBOX_TOKEN
    ) -> None:
        self.mapstyle = mapstyle
        self.token = token


def plot_cume_diagnoses(
    incidence_df: pd.DataFrame,
    block_group_gdf: gpd.GeoDataFrame,
    location_name: str,
    center: None,
    mapbox_config: MapboxConfig = MapboxConfig(),
) -> Figure:
    earliest_year = incidence_df["calendar_year"].min()
    fig = px.choropleth_mapbox(
        data_frame=incidence_df,
        geojson=block_group_gdf,
        featureidkey="properties.block_group",
        locations="block_group",
        color="cume_n_diagnosed",
        animation_frame="calendar_year",
        animation_group="block_group",
        range_color=_get_value_range(incidence_df, "cume_n_diagnosed"),
        width=700,
        height=700,
        center=center,
        zoom=5,
        labels={
            "cume_n_diagnosed": r"Cumulative<br>diagnoses",
            "calendar_year": "Year",
        },
        title=f"Diabetes diagnoses in {location_name} since {earliest_year}",
    )
    fig.update_layout(
        mapbox_style=mapbox_config.mapstyle, mapbox_accesstoken=mapbox_config.token
    )
    return fig


def _get_value_range(df: pd.DataFrame, var_name: str) -> tuple[int, int]:
    def round_to_nearest_n(x, n=10):
        return int(n * round(float(x) / n))

    return (
        round_to_nearest_n(df[var_name].min()),
        round_to_nearest_n(df[var_name].max()),
    )
