# Schelling Housing Model

## Authors

Claire Dickey (claire.dickey@epistemix.com), Tommy Nelson

## Description

The Schelling model of racial segregation in housing. This is a classic ABM that demonstrates how even slight preferences among a population for living next to others who are similar to themselves can lead to highly segregated neighborhoods.

## Conditions

**SETUP_AGENTS**

This condition removes all non-householder agents so that we only work with one agent per household. It then removes a further subset of householder agents (determined the by `frac_empty` variable) so that agents have empty householders to which they can move. It also writes the agent IDs and `my_color` variable to `agent_info.csv`. The `my_color` variable is randomly set to 0 or 1 for each agent in the `agent_startup{}` block.

**DETERMINE_BLOCK_COLOR**

This condition only utilizes the group admin agents for the block groups of the county or counties on which the simulation is run. Each day, the block group agents assess the relative number of blue and red agents living within the BG bounds and report their color fraction. If agents have moved into or out of the block group since the last update (leading to a potential change in the color fraction), the group agent moves all household agents living in the block group to the `EvaluateHappiness` state of the HAPPINESS condition. It also directs each block group agent to write the block color fractions to `block_color_history.csv` each day.

**HAPPINESS**

Householder agents use this condition to assess if the current color fraction of their block group is sufficiently self-similiar (evaluated by comparing the block group color fraction against the `desired_similarity` variable), determining if they are happy (my_happiness=1) or unhappy (my_happiness=0). After an initial assessment at the simulation start, agents only re-assess when moved into the `EvaluateHappiness` state by their block group admin agent. 

**MOVE**

Each day agents check their happiness. If they have a happiness of 0, they will remove themselves from their current block group and randomly select a new household from the list of unoccupied houses. They also record their current household and block group affiliation to `agent_house_history.csv` each day.

## Key Outputs

The visualizations included in this model utilize the following output CSVs:
- agent_info.csv: records the IDs and color of all active agents at simulation start
- block_color_history.csv: records the number of agents of each color and corresponding color fractions for each block group each day of the simulation
- agent_house_history.csv: records the household and block group of each active agent each day of the simulation

## Running this model 

This model can be run on any county, though it is more exciting when the county includes a larger number of block groups. The included visualizations for this model are currently set to focus on Kewaunee County, WI  and a .geojson showing the Kewaunee block group boundaries is included in the directory.

We encourage the user to explore how changing the `desired_similarity` variable changes the speed and degree to which neighborhoods segregate. Additionally, it is possible to change the starting fraction of red and blue agents (e.g., setting `my_color = last(sample_without_replacement(list(0,1),weights=(0.3,0.7)))`).

Possible extensions to the model include:
- increasing the number of colors to 3 or more
- adding a representation of economic mobility by assuming that unhappy agents of one color are able to move more quickly than the others