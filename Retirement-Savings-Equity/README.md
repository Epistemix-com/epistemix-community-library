# Retirement Savings Equity Model

## Authors

Noah Burrell (noah.burrell@epistemix.com)

## Description

In this model, agents accumulate (and subsequently deplete) their retirement savings according to simple rules. Then, an equity analysis is performed on the output of the model, comparing the distribution of each race in the population with the distribution of wealth owned by each race.

## Setting Up the Simulation

### Estimating Mortality Probabilities based on Demographic Characteristics
This section construts an input CSV file, `mortality_probs.csv`, which stores predicted mortality probabilities for agents of each age between 30 and 100. 

The predicted mortality probabilities are based on a method of estimating Gompertz mortality parameters from life tables from Tai and Noymer, 2017:
        [PDF](https://u.demog.berkeley.edu/~andrew/papers/tai_noymer_authorfinal.pdf);
 [Publication](https://doi.org/10.1007/s10144-018-0609-6).
        
The 2010 life table data, which is saved as CSV files (`life_table_*.csv`) in the data directory, is originally from a CDC publication: [PDF](https://stacks.cdc.gov/view/cdc/26010/cdc_26010_DS1.pdf).
       

### Assigning Educational Attainment Probabilities based on IPF
This section constructs an input CSV file, `education_probs.csv`, which stores predicted probability distributions over levels of educational attianment (No College, Some College, Associate's Degree, Bachelor's Degree, Advanced Degree) for each of six categories defined by the Cartesian product of a set of age groups (25-34, 35-54, 55+) and sex (female, male).

The distributions are computed using iterative proportional fitting (IPF) to estimate counts (which are normalized to probabilities) of educational attainment levels given age group and sex based on marginal counts of educational attainment level given age group and given set. Those target marginals are from the 
    U.S. Census Bureau, [Current Population Survey, 2010 Annual Social and Economic Supplement](https://www.census.gov/data/tables/2010/demo/educational-attainment/cps-detailed-tables.html) (Table 3).

## Conditions

**SAVING**

In this condition, agents who are at least 30 years old accumulate retirement savings at a rate of one-fifth of their annual income per year, as inspired by guidelines in the following article: https://www.nerdwallet.com/article/investing/how-much-save-by-30

Upon reaching age 65, agents retire and their savings are boosted by a factor related to behavioral biases that are correlated with their underlying demographic characteristics and educational attainment. The associations between behavioral biases and each of retirement savings and individual attributes (i.e., demographics and educational attainment) savings are drawn from the following paper by Goda et al., 2018:
[PDF](http://hdl.handle.net/10419/185222).
(Note, however, that, for simplicity, some simplifying assumptions are made in applying the work of Goda et al.)

In retirement, agents consume their savings at a constant rate (between 0.5 and 1.5 of their annual pre-retirement income per year) until they die. The rate of consumption is determined prior to the start of the simulation and is independent from any individual attributes.

**MORTALITY**

In this condition, agents who are at least 30 years old use estimated mortality probabilities to determine whether they will survive to the next year. If not, their savings are split equally among the surviving members of their Household.

## Key Outputs

The primary visualization for this model---side-by-side pie charts comparing the distribution of each race in the population with the distribution of wealth owned by each race---is constructed using data written to the following CSV file:
- `savings.csv`: records the ID, age, sex, race, income, and savings of each agent for every year during the duration of the simulation in which their age was divisible by 5.

## Running this model 
By default, this model runs in Lenoir County, North Carolina. Nothing in the simulation or analysis depends on this specific location, but it is generally recommended to run the model in a racially diverse county, so that the equity analysis of the model output is more interesting.

## References
Shah Goda, Gopi; Levy, Matthew; Flaherty Manchester, Colleen; Sojourner,
Aaron J.; Tasoff, Joshua (2018) : Predicting Retirement Savings Using Survey Measures of
Exponential-Growth Bias and Present Bias, IZA Discussion Papers, No. 11762, Institute of
Labor Economics (IZA), Bonn

Tai, T.H. and Noymer, A. (2018), Models for estimating empirical Gompertz mortality: With an application to evolution of the Gompertzian slope. Popul Ecol, 60: 171-184.