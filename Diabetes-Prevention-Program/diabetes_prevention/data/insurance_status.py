from enum import Enum
from collections import defaultdict
import re
from typing import NamedTuple

import requests

from us import states


class StateCountyData(NamedTuple):
    state_fips: str
    county_fips: tuple[str]


def get_state_county_data(state_fips: str) -> StateCountyData:
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


def get_variable_groups() -> tuple[VariableGroup]:
    """Metadata for Census variables needed to estimate health insurance
    status.

    The census often doesn't report e.g. 'total in census tract with
    private insurance'. Instead they report these values disaggregated
    by age and sex. To get total estimates by census tract, we request
    the disaggregated data and then aggregate up to get census tract
    totals. In the `ver_groups` data structure, a `VariableGroup`
    represents the concept we're looking for (e.g. `medicaid`,
    `no_insurance`). Each is associated with one or more `Variable`s
    which will be requested from the census API, and then summed for each
    census tract.
    """
    return (
        VariableGroup(
            "population",
            [
                Variable("B01003_001", "Estimate!!Total"),
            ],
            "TOTAL POPULATION",
            GeoLevel.BLOCK_GROUP,
        ),
        VariableGroup(
            "medicaid",
            [
                Variable(
                    "C27007_004",
                    "Estimate!!Total:!!Male:!!Under 19 years:!!With Medicaid/means-tested public coverage",
                ),
                Variable(
                    "C27007_007",
                    "Estimate!!Total:!!Male:!!19 to 64 years:!!With Medicaid/means-tested public coverage",
                ),
                Variable(
                    "C27007_010",
                    "Estimate!!Total:!!Male:!!65 years and over:!!With Medicaid/means-tested public coverage",
                ),
                Variable(
                    "C27007_014",
                    "Estimate!!Total:!!Female:!!Under 19 years:!!With Medicaid/means-tested public coverage",
                ),
                Variable(
                    "C27007_017",
                    "Estimate!!Total:!!Female:!!19 to 64 years:!!With Medicaid/means-tested public coverage",
                ),
                Variable(
                    "C27007_020",
                    "Estimate!!Total:!!Female:!!65 years and over:!!With Medicaid/means-tested public coverage",
                ),
            ],
            "MEDICAID/MEANS-TESTED PUBLIC COVERAGE BY SEX BY AGE",
            GeoLevel.TRACT,
        ),
        VariableGroup(
            "medicare",
            [
                Variable(
                    "C27006_004",
                    "Estimate!!Total:!!Male:!!Under 19 years:!!With Medicare coverage",
                ),
                Variable(
                    "C27006_007",
                    "Estimate!!Total:!!Male:!!19 to 64 years:!!With Medicare coverage",
                ),
                Variable(
                    "C27006_010",
                    "Estimate!!Total:!!Male:!!65 years and over:!!With Medicare coverage",
                ),
                Variable(
                    "C27006_014",
                    "Estimate!!Total:!!Female:!!Under 19 years:!!With Medicare coverage",
                ),
                Variable(
                    "C27006_017",
                    "Estimate!!Total:!!Female:!!19 to 64 years:!!With Medicare coverage",
                ),
                Variable(
                    "C27006_020",
                    "Estimate!!Total:!!Female:!!65 years and over:!!With Medicare coverage",
                ),
            ],
            "MEDICARE COVERAGE BY SEX BY AGE",
            GeoLevel.TRACT,
        ),
        VariableGroup(
            "private",
            [
                Variable(
                    "B27002_004",
                    "Estimate!!Total:!!Male:!!Under 6 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_007",
                    "Estimate!!Total:!!Male:!!6 to 18 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_010",
                    "Estimate!!Total:!!Male:!!19 to 25 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_013",
                    "Estimate!!Total:!!Male:!!26 to 34 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_016",
                    "Estimate!!Total:!!Male:!!35 to 44 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_019",
                    "Estimate!!Total:!!Male:!!45 to 54 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_022",
                    "Estimate!!Total:!!Male:!!55 to 64 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_025",
                    "Estimate!!Total:!!Male:!!65 to 74 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_028",
                    "Estimate!!Total:!!Male:!!75 years and over:!!With private health insurance",
                ),
                Variable(
                    "B27002_032",
                    "Estimate!!Total:!!Female:!!Under 6 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_035",
                    "Estimate!!Total:!!Female:!!6 to 18 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_038",
                    "Estimate!!Total:!!Female:!!19 to 25 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_041",
                    "Estimate!!Total:!!Female:!!26 to 34 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_044",
                    "Estimate!!Total:!!Female:!!35 to 44 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_047",
                    "Estimate!!Total:!!Female:!!45 to 54 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_050",
                    "Estimate!!Total:!!Female:!!55 to 64 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_053",
                    "Estimate!!Total:!!Female:!!65 to 74 years:!!With private health insurance",
                ),
                Variable(
                    "B27002_056",
                    "Estimate!!Total:!!Female:!!75 years and over:!!With private health insurance",
                ),
            ],
            "PRIVATE HEALTH INSURANCE STATUS BY SEX BY AGE",
            GeoLevel.TRACT,
        ),
        VariableGroup(
            "no_insurance",
            [
                Variable(
                    "B27010_017",
                    "Estimate!!Total:!!Under 19 years:!!No health insurance coverage",
                ),
                Variable(
                    "B27010_033",
                    "Estimate!!Total:!!19 to 34 years:!!No health insurance coverage",
                ),
                Variable(
                    "B27010_050",
                    "Estimate!!Total:!!35 to 64 years:!!No health insurance coverage",
                ),
                Variable(
                    "B27010_066",
                    "Estimate!!Total:!!65 years and over:!!No health insurance coverage",
                ),
            ],
            "TYPES OF HEALTH INSURANCE COVERAGE BY AGE",
            GeoLevel.BLOCK_GROUP,
        ),
    )
