import geopandas as gpd


def get_state_census_tract_gdf(state_fips: str) -> gpd.GeoDataFrame:
    return gpd.read_file(_get_census_tract_shp_url(state_fips)).pipe(
        _format_census_tract_shp
    )


def _get_census_tract_shp_url(state_fips: str) -> str:
    return (
        "https://www2.census.gov/geo/tiger/GENZ2022/shp/"
        f"cb_2022_{state_fips}_tract_500k.zip"
    )


def _format_census_tract_shp(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Select, combine, and rename columns."""
    name_map = {"GEOID": "census_tract"}
    select_cols = [x for x in name_map.values()] + ["county_fips", "geometry"]
    return (
        gdf.assign(county_fips=lambda df: df["STATEFP"].str.cat(df["COUNTYFP"]))
        .rename(columns=name_map)
        .loc[:, select_cols]
    )
