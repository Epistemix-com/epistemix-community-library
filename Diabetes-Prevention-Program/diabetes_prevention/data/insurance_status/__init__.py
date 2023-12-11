from census import Census

import pandas as pd

from diabetes_prevention.data.insurance_status.census_lib import (
    Variable,
    VariableGroup,
    GeoLevel,
    get_census_tract_data,
)
from diabetes_prevention.data.insurance_status.geo import get_state_census_tract_gdf


def get_insurance_status_prob_df(census: Census, state_fips: str) -> pd.DataFrame:
    var_groups = get_variable_groups()
    target_cols = [x.name for x in var_groups if x.name != 'population']
    return (
        get_census_tract_data(census, var_groups, state_fips)
        .assign(tot=lambda df: df[target_cols].sum(1))
        .pipe(lambda df: (
            df.assign(**{
                c: df[c] / df['tot'] 
                for c in target_cols
            })
        ))
        .loc[:, ['census_tract'] + target_cols]
    )


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
    )
