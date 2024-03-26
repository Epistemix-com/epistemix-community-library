# Asthma Events Model

## Authors

Claire Dickey (claire.dickey@epistemix.com)

## Description

A model that gives some agents an asthma attribute, and triggers asthma events based on the input daily air quality (AQI). 

## Model Components

The `ASTHMA` condition assigns asthma risk to all agents in households based on age, sex, and race. This model makes use of the `Read_Attribute.fredmod`, which allows for the in-simulation generation of new attributes for agents as a function of existing agent attributes. In this case, we are using as input the fraction of the population that has been diagnosed with asthma as a function of sex, age, and race (https://www.cdc.gov/asthma/most_recent_national_asthma_data.htm). Once agents have their asthma likelihood, they are then assigned to have or not have asthma with `prob(my_asthma_risk)`. This means that the simulation should return a realistic overall distribution of asthma prevalence, without hardcoding specific agents to have asthma prior to each run. For more information on the use of `Read_Attribute` feature, see the External Data example in the Special Topics of the Quickstart Guide.

The `ENVIRONMENT` condition updates the Asthma Quality Index (AQI) each day, based on daily data recorded Minneapolis for 2023, pulled from https://www.epa.gov/outdoor-air-quality-data/air-quality-index-daily-values-report. AQI serves as a proxy for perilous air pollution conditions which are shown to increase the frequency of acute asthma events (with a lead time of approximately 24 hours: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9278633/).

Each day of the simulation, agents with asthma check the local daily air conditions to assess their risk of experiencing an acute asthma event. Acute events are more likely with high AQI, and also with higher household elevation.

Agents who experience an event seek care at their nearest hospital (locations of US hospitals pulled from: https://www.shepscenter.unc.edu/programs-projects/rural-health/list-of-hospitals-in-the-u-s/), and recover fully after twenty four hours.

## Outputs

Agents' asthma risk and status are recorded in `agent_info.csv`. A record of discrete asthma events, the daily AQI, and the associated hospital are stored in `asthma_events.csv`.

