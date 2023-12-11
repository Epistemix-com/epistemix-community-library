"""Utility functions and data structures used for interacting with the
`census` client.


The way census data is organized tends to require some aggregation to
achieve values of interest. E.g. variable `C27007_004` is males under
19 years with medicaid, `C27007_007` is males 19-64 years with
medicaid... No variable speficies 'total people with medicaid'.

The `get_census_tract_data` function defined here accepts an iterable
of `VariableGroup` objects of interest. `VariableGroup`s are collections
of census variables whose values should be summed together to obtain
a quantity of interest. The DataFrame returned by `get_census_tract_data`
will have `VariableGroup.name` values as column names. This allows queries
on the census to be defined declaritively as data structures composed of
`VariableGroup`s.
"""

from enum import Enum
from collections import defaultdict
from itertools import chain
import re
from time import sleep
from typing import NamedTuple, Iterable

import requests

import numpy as np
import pandas as pd

from us import states

from census import Census


class StateCountyData(NamedTuple):
    state_fips: str
    county_fips: tuple[str]


def _get_state_county_data(state_fips: str) -> StateCountyData:
    """Get list of county fips codes for a state from the 2020 US census
    website.

    Examples
    --------
    >>> get_state_county_data("50")
    StateCountyData(state_fips='50', county_fips=('001', '003', '005', '007', '009', '011', '013', '015', '017', '019', '021', '023', '025', '027'))
    """
    data = _download_state_counties_data(state_fips)
    return _parse_state_counties_data(data)


def _download_state_counties_data(state_fips: str) -> str:
    def get_state_counties_url(state_fips: str) -> str:
        state_abbr = states.mapping("fips", "abbr")[state_fips].lower()
        return (
            "https://www2.census.gov/geo/docs/reference/codes2020/cou/"
            f"st{state_fips}_{state_abbr}_cou2020.txt"
        )

    return requests.get(get_state_counties_url(state_fips)).text


def _parse_state_counties_data(data: str) -> StateCountyData:
    regex = re.compile("^[A-Z]{2}\|([0-9]{2})\|([0-9]{3}).*$")
    matches = (m for m in (regex.match(d) for d in data.split("\n")) if m is not None)
    states_counties = ((m.group(1), m.group(2)) for m in matches)
    d = defaultdict(list)
    for sc in states_counties:
        d[sc[0]].append(sc[1])
    if (d_len := len(d.keys())) != 1:
        raise ValueError(
            f"Expected data for one state in response for state {state_fips} "
            f"but found {d_len}"
        )
    state_fips = list(d.keys())[0]
    return StateCountyData(state_fips, tuple(sc for sc in d[state_fips]))


class GeoLevel(Enum):
    BLOCK_GROUP = 0
    TRACT = 1


class Variable(NamedTuple):
    name: str
    label: str


class VariableGroup(NamedTuple):
    name: str
    variables: list[Variable]
    concept: str
    geo_level: GeoLevel


def get_census_tract_data(
    census: Census, var_groups: Iterable[VariableGroup], state_fips: str
):
    census_variable_names = tuple(
        f"{v.name}{'E'}" for v in chain(*(vg.variables for vg in var_groups))
    )
    dat_df = pd.concat(
        [
            (
                pd.DataFrame.from_records(
                    _download_census_tract_var_data(
                        census, census_variable_names, state_fips, county_fips
                    )
                )
                .assign(
                    census_tract=lambda df: df["state"]
                    .str.cat(df["county"])
                    .str.cat(df["tract"])
                )
                .drop(columns=["state", "county", "tract"])
            )
            for county_fips in _get_state_county_data(state_fips).county_fips
        ]
    )

    raw_var_cols = [x for x in dat_df if x != "census_tract"]
    for vg in var_groups:
        dat_df = dat_df.pipe(
            lambda df: df.assign(
                **{vg.name: df[[f"{v.name}{'E'}" for v in vg.variables]].sum(1)}
            )
        )

    keep_cols = ["census_tract"] + [vg.name for vg in var_groups]
    return dat_df[keep_cols]


def _download_census_tract_var_data(
    census: Census,
    var_names: tuple[str],
    state_fips: str,
    county_fips: str,
    delay: bool = True,
):
    def delay_time():
        return 2.0 + np.random.uniform(-0.5, 0.5)

    if delay:
        sleep(delay_time())
    return census.acs5.get(
        var_names,
        geo={"for": "tract:*", "in": f"state: {state_fips} county: {county_fips}"},
    )
