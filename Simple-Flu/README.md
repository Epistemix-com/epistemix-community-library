# Simple Flu

## Authors

Claire Dickey (claire.dickey@epistemix.com)

## Description

A model that represents the spread of influenza throughout a population, characterized with a compartmental Symptomatic-Exposed-Infectious-Recovered (SEIR) model. At the beginning of the simulation, 10 randomly selected agents are exposed to influenza. Exposed agents become infectious after an average of two days, and they can either be Symptomatic (66%) or Asymptomatic (33%). Agents remain infectious for an average of 5 days, during which they can transmit the disease to other susceptible agents that they come into contact with. 
After the infectious period, they recover and are no longer susceptible to reinfection. Agents also record where they received their exposure.

## Conditions

**RESP_DISEASE**

The transmissible condition that represents a simple flu. The starting number of exposures is set by the Import state: `import_exposures(RESP_DISEASE,10)`. All agents begin as susceptible. 

**RECORD_EXPOSURES**

Agents who enter the Exposed state of RESP_DISEASE also record where they received their exposure (e.g., workplace, household, etc).

![Dot Placeholder](./images/placeholder.png)
![No Dot Placeholder](images/placeholder.png)

## Key outputs

Traditional epi curves can be created from default outputs from the RESP_DISEASE condition, which records how many agents are newly entering a state each. To get geospatial information on where infections are occuring, agents record their exposure in `exposure_locs.csv`, along with the relevant lat/lon.



