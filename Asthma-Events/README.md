# Asthma Events Model

## Authors

Claire Dickey (claire.dickey@epistemix.com)

## Description

A model that gives some agents an asthma attribute, and triggers asthma events based on the input daily air quality (AQI). 

## Model Components

The `ENVIRONMENT` condition updates the AQI each day, based on daily data recorded Minneapolis for 2023. AQI serves as a proxy for perilous air pollution conditions which are shown to increase the frequency of acute asthma events (with a lead time of approximately 24 hours).

The `ASTHMA` condition assigns asthma risk to all agents in households based on age, sex, and race. Once agents have their individualized risk score, they are then assigned to have or not have asthma with `prob(my_asthma_risk)`.

Each day of the simulation, agents with asthma check the local daily air conditions to assess their risk of experiencing an acute asthma event. Acute events are more likely with high AQI, and also with higher household elevation.

Agents who experience an event seek care at their nearest hospital, and recover fully after twenty four hours.

## Outputs

Agents' asthma risk and status are recorded in `agent_info.csv`. A record of discrete asthma events, the daily AQI, and the associated hospital are stored in `asthma_events.csv`.

