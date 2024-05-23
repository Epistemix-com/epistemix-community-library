# Epistemix Community Model Library
Welcome to the Epistemix Model Library. Here you can browse the ready-made models that are available for use in the Epistemix Platform. For information about how to access these models within the Platform IDE, as well as how to contribute your own models, see our [documentation](https://docs.epistemix.com).

## Models
The models contained within this repository span multiple use-cases and can serve as a great starting point for your custom models.

* [Asthma Events](Asthma-Events/README.md) - A model that gives some agents an asthma attribute, and triggers asthma events based on the input daily air quality (AQI). 
* [Epstein Rebellion Model Geospatial](Epstein-Rebellion-Model-Geospatial/README.md) - This model captures the evolution of civil violence in a population split into regular agents, who are disaffected and willing to rebel if the conditions are right, and cop agents, who try to quell rebellion by jailing those agents. In this implementation, the households of Grand Isle County, VT serve as the locations between which agents move.
* [Epstein Rebellion Model Grid](Epstein-Rebellion-Model-Grid/README.md) - This model captures the evolution of civil violence in a population split into regular agents, who are disaffected and willing to rebel if the conditions are right, and cop agents, who try to quell rebellion by jailing those agents. In this implementation, agents move across a simple grid.
* [Finding a Local Doctor](Finding-a-Local-Doctor/README.md) - The Dr Office modernisation efficiency model is a FRED demonstration model exploring the effect of modernisation of healthcare services on healthcare outcomes.
* [Ground Shipping Logistics](Ground-Shipping-Logistics/README.md) - This model represents a ground transportation network. Cities represent nodes in the network and roads are edges. A table of trucks agents is read in at the beginning of the simulation. There are no human agents in the model. 
* [In Store Transactions](In-Store-Transactions/README.md) - This FRED model has all agents 18 and older go shopping. The number of stores,  items available, and item prices are specified in `/data/item_inventory_TRANSACTIONS.csv`. The job will print out receipts as agents shop at their chosen stores.
* [Misinformation Model](Misinformation-Model/README.md) - This model begins by building a network to represent day-to-day in-person interactions between agents. It starts by stepping through the agents' daily schedules (as determined in the synthetic population) and randomly selecting other agents from "interaction pool" (e.g., the workplace, the block group) to become network links. 
* [Monkeypox Outbreak](Monkeypox-Outbreak/README.md) - Modeling a Monkeypox outbreak in Allegheny County, where transmission specifically occurs in bathhouses.
* [Non-Geospatial Schelling](Non-Geospatial-Schelling/README.md) - In this set of models, we explore the following question: How (if at all) do the dynamics of the classic Schelling model of residential segregation change if we change the topology of the network that determines what constitutes a "neighborhood"?
* [Retirement Savings Equity](Retirement-Savings-Equity/README.md) - In this model, agents accumulate (and subsequently deplete) their retirement savings according to simple rules. 
* [Schelling Housing Model](Schelling-Housing-Model/README.md) - The Schelling model of racial segregation in housing. This is a classic ABM that demonstrates how even slight preferences among a population for living next to others who are similar to themselves can lead to highly segregated neighborhoods.
* [Simple Flu](Simple-Flu/README.md) - A model that represents the spread of influenza throughout a population, characterized with a compartmental Symptomatic-Exposed-Infectious-Recovered (SEIR) model.
* [Water Usage](Water-Usage/README.md) - The objective of the water usage app model is to simulate household water use.


## Using The Models
These models are automatically included in your [Epistemix Platform IDE](https://docs.epistemix.com/platform/getting-started/#platform-ide) home directory. After you launch your IDE, you can find the models in the `Community Library` folder. For more information see the [Accessing the Community Library](https://docs.epistemix.com/platform/community-library/#accessing-the-community-library) section of our documentation.

## Contributing Your Models
We encourage everyone who wants to contribute their models to the Community Library to do so. Please follow the [instructions for contributing here](https://docs.epistemix.com/platform/community-library/#library-submission-guidelines).

### Dockerfile

We include a Dockerfile to help with administrative tasks like dependency
management. To start the dev environment run

```shell
scripts/dev
```

### Updating dependencies

Abstract Python dependencies are specified in the file `requirements.in`. These
are the names of packages used in the Community Library tutorials without pinned
(`==`) version numbers. We use [pip-tools](https://github.com/jazzband/pip-tools)
to generate concrete dependencies (including specific versions of the
dependencies of our named dependencies) in `requirements.txt` from the abstract
`requirements.in` file. The process for adding a dependency is:

1. Add the name of the new dependency to `requirements.in`
2. From within the `dev` container run `scripts/update-requirements`
3. Commit changes to both `requirements.in` and `requirements.txt` to version
   control.

### Deployment
The `generate-manifest.sh` file is executed when a commit is pushed to the main or production branch.  There is a github action workflow that syncs the contents of the manifest to an S3 bucket and consumed by downstream services.  The main branch publishes to the development environment and the production branch publishes to the production environment, with corresponding S3 buckets `dev-model-library-assets` and `prod-model-library-assets`.

### Adding a new .toml file

When adding a new toml file, it's important to include a `banner` key with a reference to an Epistemix logo png file.  You can find examples of this in the current Community Models as of 4/4/24. 