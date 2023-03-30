# Monkeypox Outbreak

## Authors

Tommy Nelson

## Description

Modeling a Monkeypox outbreak in Allegheny County, where transmission specifically occurs in bathhouses. The model has a subset of the msm population visit bathhouses on a regular schedule. Agents select a candidate sexual partner from the other attendees of the bathhouse on a given day. In a sexual encounter, an infected agent can transmit monkeypox to their partner. Agents may have multiple partners per visit, if they are selected by others, but every agent only chooses one partner per visit. Agents also test for monkeypox upon the emergence of symptoms and report their cases.

## Conditions

**BATHHOUSE**

A place type called BathHouse is declared and a list of sites is read in on startup. The BATHHOUSE condition applies only to MSM agents. Some fraction of MSM agents attend bathhouses.  The specific bathhouse visited is selected at random each time. The time between visits also varies randonly. During a visit, the agent selects another visitor randomly for an encounter. The bathhouse group agent keeps track of the number of weekly visits and encounters.

** MPOX **

This condition describes the SEIR stages of Monkeypox infection. This is not a respiratory virus, so we don't use built in transmission. Virus transmissibility and susceptability are manually set.

** TEST_REPORT **

A fraction of agents who become symptomatic decide to test themselves and report positive cases.


## How to use



Future work: Each encounter may result in monkeypox transmission. The probability of transmission should depend on each agent's current state in a separate MONKEYPOX condition, which may set the agent's transmissibility, susceptibility, vaccination status, etc. 

Possible intervention targets:
- the fraction of msm who visit bathhouses.
- the transmissibility within a given bathhouse.
- the agent's preferences for safer bathhouses.
- the closure of unsafe bathhouses.
- vaccine uptake
- use of preventive measures by individual agents