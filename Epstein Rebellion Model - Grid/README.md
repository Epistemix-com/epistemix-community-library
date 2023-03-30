# Epstein Rebellion Model

## Authors

Claire Dickey (claire.dickey@epistemix.com)

## Description

This model captures the evolution of civil violence in a population split into regular agents, who are disaffected and willing to rebel if the conditions are right, and cop agents, who try to quell rebellion by jailing those agents.

In this implementation, agents move across a simple grid, making a single move each day. Based on their close neighbors (determined by the vision parameter), they assess if their personal grievance is higher than their risk of being arrested (determined by the ratio of already rebelling agents to cops in the neighborhood).

## Conditions

**GENERATE_LOCATIONS**

Loads in the world grid and the regular and cop agents (which need to generated with the code provided in `epstein-rebellion-model-grid.ipynb`).

**PLACE_AGENTS**

Condition for recording which grid cells are visible from each other. Determined by the `agent_vision` variable (default: 7 grid cells)

**REGULAR_AGENTS**

The behavior loop for regular agents. Each day, regular agents move to a new, unoccupied grid cell within their vision range. There, they assess the number of neighboring agents who are in open rebellion versus the number of cop agents in range, which represents their `estimated_arrest_probability`. Agents compare this value to their own grievance level: `perceived_hardship * (1-government_legitimacy)` to determine if they will rebel.

If jailed by a cop, agents become inactive and remain in the jailed state for 1 to `max_jail_term` days.

**COP_AGENTS**

The behavior loop for cop agents. Each day, cop agents move to a new, unoccupied grid cell within their vision range and look for one rebelling agent to jail.


## Key Outputs

- regular_agent_info.csv: reports the personal variables of each agent (`perceived_hardship` and `grievance`) as well as the number of cops and rebelling agents within each regular agent's neighborhood.
- movement.csv: tracks the location and status of each agent (cop and regular) each day of the simulation.

## How to use

This model requires pregenerating the grid and the distribution of cop vs regular agents. This is done by running the code included in the Agent Startup section of `epstein-rebellion-model-grid.ipynb`.

Population variables
- simulation grid size: 40x40
- agent density: 0.7
- cop density: 0.05

World state variables
- government legitimacy: 0.7
- max jail sentence: 15 days
- agent vision: 7
- rebellion threshold: 0.1
