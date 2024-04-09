# Retirement Savings Equity Model

## Authors

Noah Burrell (noah.burrell@epistemix.com)
Benjamin Panny (BMP83@pitt.edu)

## Description

In this set of models, we explore the following question: How (if at all) do the dynamics of the classic Schelling model of residential segregation change if we change the topology of the network that determines what constitutes a "neighborhood"?

## Setting Up the Simulation

### Procedurally Generating Agents
In this simulation, since the model does not involve any agent attributes from the synthetic population (including geospatial locations), the agents are read in from a temporary file that is procedurally generated using Python in the notebook environment. Accordingly, the `location` and `default_model` parameters in the `simulation` block are set to `none`. (For this family of related models, the simulation block and other startup code that is shared among all the model versions is contained in the file **`core.fred`**.)  

## Conditions

**SETUP_NETWORK**
This condition sets up the network (called `Friendship`) that is used to define the set of agents that comprise a central agent's "neighborhood."
This happens in two phases:
(1) A network is built where all of the agents have 8 neighbors (or 8 neighbors on average). 
(2) The network is "pruned", so that there are "empty spots" that can be filled with new neighbors as agents rewire their connections to try to achieve satisfaction with their neighborhood.

There are three total versions of this condition, each contained in a separate file:
- In **`setup_network_grid.fred`**, the `SETUP_NETWORK` condition creates a grid network, as in the classic Schelling model. Similarly, the effect of the pruning step is to create "holes" in the grid that can be filled by an agent moving to an empty location. (The logic that implements this behavior is to build a complete grid with "extra" agents and then have those extra agents exit the simulation prior to the start of the action. As such, the model is dependent on the particular initializion code that generates the agent file in the notebook environment. Changing the number of agents, or the fraction of empty spaces, would necessitate updating this logic.)
- In **`setup_network.fred`**, the `SETUP_NETWORK` condition creates a [random graph](https://docs.epistemix.com/fred-reference/r/randomize_network/), where the mean degree is equal to 8. The pruning step iterates over the edges in the graph and decides whether to remove it independently at random with probability `edge_drop_prob`, which is set in **`core.fred`**.
- In **`setup_network_local.fred`**, the `SETUP_NETWORK` condition creates a [random graph](https://docs.epistemix.com/fred-reference/r/randomize_network/), where the mean degree is equal to 8, as in **`setup_network.fred`**. However, the pruning step follows the logic of the grid, where it creates "holes" in the network by removing "extra" agents (and their associated edges) that are included when constructing the network.

**HAPPINESS**
In this condition, agents evaluate their satisfaction with their neighborhood composition---by comparing the fraction of their neighbors that share their color and comparing that with their `desired_similarity`, which is set in **`core.fred`**. Unhappy agents "move" by rewiring their connections in the `Friendship` network in a manner that depends on the specific version of the model (see the `REWIRE` condition, below).

**REWIRE**
This condition govens the logic by which unhappy agents "move" (i.e., reconstitute their neighborhood) in the network.
- In **`rewire_grid.fred`**, agents delete all their edges (leaving a "hole" in their previous location) and move to a new "hole" in the grid, where they add an edge in the `Friendship` network to each agent adjacent to their new location in the grid.
- In **`rewire_one_link.fred`**, agents delete a single edge to an agent who does not share their color and add a new edge to a random agent with an empty spot in their neighborhood.
- In **`rewire_all_links.fred`**, agents delete all of their edges and, for each edge that was deleted, adds a new edge to a random agent with an empty spot in their neighborhood.
- In **`rewire_all_links_local.fred`**, agents delete all of their edges. Then, as an analogy to how agents rewire on a grid, an agent:
(1) chooses a new "central neighbor" with an empty spot for a new connection and creates an edge to that agent,
(2) replaces the rest of the edges that were deleted by connecting to agents with empty spots for new connections within the _k_-hop neighborhood of the central neighbor for the smallest _k_ such that it is possible to replace every remaining deleted edge. Among the eligible agents (i.e., those with empty spots for new connections within the _k_-hops of the central neighbor), new connections are formed preferentially, proportial to their (squared) shortest path distance from the central neighbor.

## Key Outputs

The primary visualizations for this model---animations that illustrates how neighborhood composition changes in the population of agents over time for each version of the model---are constructed using the network output that is recorded by the FRED simulation engine each day of the simulation, because `output_interval = 1` is set for the `Friendship` network in each of the files containing a version of the `SETUP_NETWORK` condition. Since agent attributes are assigned using Python in the notebook environment prior to executing a simulation, there is no need to record/access agent attributes with a simulation output file. Instead, these are recorded in the notebook environment in the `attributes` dictionary and used in constructing the visualizations.

## Running this model 
The accompanying notebook will walk you through running the different model versions and and visualizing their results. There is also a detailed textual component to lead you through the narrative of how we arrived at the different model versions that we explore and what the key takeaways are from each of them.