# Water usage model

## Authors
Paige Miller, Noah Burrell

## Description

The objective of the water usage app model is to simulate household water use. We assume there are 5 main water use activities: watering the lawn, showering, cleaning, eating, and using the toilet. The model has two components: an activity component that describes how much water households use based on the household composition of adults and children and a reporting component.  The model prints a csv of household usage grouped by block group. 


## Conditions: 

- WATERACTIVITY: A condition that describes household water usage
- REPORT_USAGE: A condition that reports household water usage

## Extensions

The model could be extended by adding in threshold water usage: 

The idea would be that if a threshold in an area is reached then the area goes into “restriction” and it doesn’t get out of restriction until the usage is below the threshold for a certain amount of time. In the restriction, households are assigned “my_limitation_propensity” and this determines the probability that each month they are likely to listen to restrictions and actually reduce their consumption. 

* Set threshold for block groups based on average of previous months (e.g., 105%) and if exceeds then go under restriction. Make a condition for describing if the area is under restriction based on area consumption. 
* Group agent for area (block group agent) produces an indicator variable
* At beginning of each month, HH asks block group, if yes, and if not already under restriction then flip our my_restriction_propensity coin and adjust constants if decides to limit consumption
* To get out of restriction, block group needs to be under the average of the previous few months 
* If this doesn’t work, can make restrictions random and then get out of restriction have consumption be 95% of previous 3 months

Alternatively, the model could be adapted to include sustainable practices as a transmissible condition -- in other words, being sustainable spreads in a population like a disease or an idea. 

