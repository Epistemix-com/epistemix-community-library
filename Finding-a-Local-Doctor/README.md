# Finding a Local Doctor

## Authors
Jessica McQuade

## Description

The Dr Office modernisation efficiency model is a FRED demonstration model exploring the effect of modernisation of healthcare services on healthcare outcomes. At the individual level the model tracks personal health changes over time. Ideally, when patients become sick they try to access their local GP to resolve moderate health issues. For severe cases patients instead access the ED. 

A failure in the market can occur due to constraints in the system. An individual may ony visit their local GP and must 'queue' for an appointment on the day of their illness with all other individuals who need access to a Dr appointment that day. The number of avialable appointments on any given day is dictated by the 'modernity' of the office; whether the office can offer online, phone or only in-person apppointments. The more 'modern' the office, the greater the number of available appointments due to efficiency savings in online consulations. 

#### Individual actions:

Whilst a Dr Office may offer a range of appointments, individuals make their own choices based on their preferences. Person A may be happy to take any appointment they can get whilst Person B may only accept an in-person appointment. So what happens when Person B cannot access the in-person appointment they require? They get impatient. 

The threshold for impatience increases when a person's health is worse. For example, a person with health status 'mild' will attempt to book an appointment at their local Dr Office more days in a row before becoming impatient that someone with health status 'moderate'.

#### Population level outcomes:

When a person becomes impatient, they take accessing healthcare into their own hands and visit ED! The interplay between individual choices and Dr Office logistics lead to a global outcome of more (or less) incorrect visits to the ED affecting global waiting times for severe cases.

#### Some key model assumptions:

* Households only try to access appointments at their nearest Dr Office
* Households only try to access one appointment choice at the start of the day and do not rejoin the queue 
* The young and the elderly are more likely to be more severely ill


## Conditions

** CONFIGURE_DR_OFFICE **

A condition that reads in data for  and generates dr office locations and appointments based on characteristic size and modernity.

** CONFIGURE_AGENT_HEALTH **

A condition that configures an agent's initial health status. Those older than 60 or younger than 10 are more likely to have poorer initial health.

** GET_LOCAL_DR_OFFICE **

A condition that assigns a DrOffice location to an agent. Offices are assigned based on geographical proximity.

** HEALTH_UPDATE **

A condition that updates an agents health. In response, agents choose whether or not to access different healthcare options depending on the availability of appointments, their health status and their impatience.

## Key outputs

- local_dr_office_assignment.csv: records the location of each agent's hosuehold and which doctor's office they selected at the outset of the simulation
- agent_at_ED.csv: records when agents go to an Emergency Department and how many attempts they made to access care prior
- agent_health_tracks.csv: tracks when agents are healthy vs sick
