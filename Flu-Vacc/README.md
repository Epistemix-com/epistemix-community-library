# FluVacc Model

## Authors

Noah Burrell (noah.burrell@epistemix.com)

## Description

This model is an adaptation of a model originally implemented using NetLogo (Vardavas et al., 2007; Vardavas and Marcum, 2013). Alongside the model code, the NetLogo implementation provides the following description:

> **WHAT IS IT?**
> 
> This Netlogo agent-based model (ABM) implements a modified version of the Vardavas et al., 2007 inductive reasoning adaptive decision-making model of seasonal influenza vaccination that was inspired by Minority Game methodology. The model was analyzed and extended by Breban et al., 2007 and Vardavas and Marcum, 2013.
>
> In the original model by Vardavas et al., 2007, considered a population of N individuals acting in their own self-interest who do not communicate their vaccination decisions to each other. Every flu season, these individuals independently decide whether or not to get vaccinated against influenza using a highly effective vaccine that is risk-free and is percieved as risk-free. Individuals in the model are characterized by two biological attributes (adaptability and memory) that they use when making vaccination decisions. Individuals can adapt their vaccination behavior for the current season on the basis of their memories of the consequences of their past vaccination decisions: i.e., they use cognition to make decisions. The individual-level model of adaptive decision-making was coupled to a susceptible-infected-recovered (SIR) model of seasonal influenza disease transmission dynamics in presence of vaccination.
>
> **HOW IT WORKS**
> 
> What is novel here is:
> 
> i) We implement the model on a lattice that includes sites with long-range interactions to other sites within a given radius, which we call a clustered hub lattice.
> 
> ii) In the original model, those who vaccinated and were not-infected evaluated their decision of vaccination on the basis of whether or not an epidemic occured. This was based whether or not the vaccination coverage had exceeded the crictial vaccination coverage required for herd-immunity calulated from 1- 1/R0 where R0 is the basic reproductive number used in the SIR transmission model. Here, individuals have a threshold of the percentage of infected individuals. If by the end of the season the cumulative number of infected is below this threshold, those who vaccinated evaluate their decision on the basis that there wasn’t a serious epidemic and vaccination wasn’t necessary.
> 
> iii) The original model was extended by Vardavas and Marcum, 2013 to run on various network structures. Here, for ease of visualization, we choose to use a simple network represented by a regular lattice which was not considered by Vardavas and Marcum, 2013. However, our regular lattice has long range interactions that are geographically local due to the constraint of the radius. The frequency of the long-distance interactions (i.e., the long range edges connecting sites) is chosen to follow a power-law or a semi-power-law. As we are unaware of the name for this type of lattice, we call it a clustered hub lattice.

### Implementation in the FRED Modeling Language: Synthpop FluVacc
A key difference between the NetLogo implementation(s) and this implementation is that the agents in this implementation come from the Epistemix Synthetic Population of the United States. As a result, transmission of the flu occurs on the implicit, proximity-based social network that results from the interactions of agents who appear at the same places (at the same times) during the course of the simulation, rather than on an explicit social network whose structure is defined in the model code itself.

The notebook in the `exercise` subdirectory invites you to explore freely the transmission network that results from a simulation of the FRED modeling language implementation and consider the differences between that network and those considered in the NetLogo implementation(s) of this model.

## Conditions

**INFLUENZA**

This condition (in the `flu_season_transmission.fred` file) applies the standard SEIR framework to facilitate an annual flu season in the model. A given number of infections (`num_initial_infections`) is introduced into the population on January 1st of every simulated year.


**VACCINATION**

This condition (in the `update_behavior.fred` file) implements the adaptive behavioral model for vaccine uptake first proposed by Vardavas et al., 2007.


**RECORD\_HOUSEHOLD\_LOCATION/RECORD_OUTCOMES**

These conditions (in the `record.fred` file) each produce a CSV output file (`household.csv` and `outcomes.csv`, respectively), which are used to create an animation (see below).


## Key Outputs

The `RECORD_HOUSEHOLD_LOCATION` and `RECORD_OUTCOMES` conditions in `record.fred` each produce a CSV output file. These are used to create an animation in the `flu_vacc.ipynb` notebook that is analogous to the visualization produced by the NetLogo implementation of the FluVacc model. The code that implements this animation is encapsulated in the `plot_output.py` module.

The `flu_vacc.ipynb` notebook also calls a function (similarly encapsulated in the `plot_output.py` module) to create an epi-curve plot using the default output files written by the FRED simulation engine. This plot illustrates the differences in the annual flu seasons throughout the course of the simulation.
Note that this plot is interactive, so you can zoom in on a particular spike in the plot to look more closely at the behavior in a given flu season.


## References
Breban, R., Vardavas, R., Blower, S., 2007. Mean-field analysis of an inductive reasoning game: application to influenza vaccination. Phys Rev E Stat Nonlin Soft Matter Phys 76, 031127.

Vardavas, R., Breban, R., Blower, S., 2007. Can influenza epidemics be prevented by voluntary vaccination? PLoS Comput Biol 3, e85. [https://doi.org/10.1371/journal.pcbi.0030085](https://doi.org/10.1371/journal.pcbi.0030085)

Vardavas, R., Marcum, C.S., 2013. Modeling the Interplay between Human Behavior and Spread of Infectious Disease, in: d’Onofrio, A., Manfredi, P. (Eds.), . Springer Series on Behavioral Epidemiology, pp. 203–227.