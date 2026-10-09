# Urban Delivery Network Under Road Closures

## Project idea

This project studies restaurant deliveries on a small urban road network. We compare random road closures with closures of roads used by many normal delivery routes.

Our research question is:

> How do random road closures and closures of frequently used roads affect average delivery distance and customer accessibility?

We expected highest-use closures to cause more disruption because these roads support several deliveries at the start of the experiment.

## How the model works

The model is a weighted, undirected graph made with Python and NetworkX.

- 36 locations in a 6 by 6 grid
- 60 two-way roads
- 3 restaurants at `(0, 0)`, `(5, 5)` and `(0, 5)`
- 15 customers spread across the network
- One fixed distance from 1 to 5 units for each road

The grid gives several possible routes but is still small enough to check visually. Three restaurants avoid making every delivery depend on one starting point. The 15 customer locations were selected across the grid so different parts of the network are used.

The customer nodes are `(0, 2)`, `(0, 4)`, `(1, 1)`, `(1, 3)`, `(1, 4)`, `(2, 0)`, `(2, 2)`, `(2, 5)`, `(3, 0)`, `(3, 3)`, `(4, 1)`, `(4, 2)`, `(4, 4)`, `(5, 2)` and `(5, 4)`.

The road distances are generated once using seed 42. Different roads can have different distances, but their values stay unchanged during a comparison. Each customer is first assigned to the restaurant with the shortest weighted distance. NetworkX then calculates the shortest delivery path.

## Finding frequently used roads

We calculate all delivery routes before any road closes. This is the baseline. For every road, the code counts how many baseline routes use it.

Roads are ranked from highest to lowest usage. If roads have the same count, their coordinates are used as a reproducible tie-break. Because that tie-break can affect the result, the project also tests every road tied at the fourth closure position.

## Experiments

We close 1, 2, 3, 4, 5, 6, 8 and 10 roads. At every level we compare:

1. Random closures, repeated 100 times with recorded seeds.
2. Closures following the baseline highest-use ranking.

The main measurements are average delivery-distance increase and percentage of customers reachable.

We report two service rules:

- **Fixed assignment:** an order stays with its original restaurant.
- **Restaurant reassignment:** if the original restaurant is cut off, the customer can use the nearest restaurant that still has a path.

The second rule separates a failed restaurant assignment from a customer who is physically disconnected from every restaurant.

Extra checks include different road-distance seeds, tied-road choices and a static travel-cost multiplier. The cost multiplier is only a simple sensitivity check. It is not a full traffic simulation and is not treated as delivery time.

The main random comparison uses 100 repetitions so its distribution is visible. The ten-seed check uses 50 repetitions for each seed, giving 500 additional random runs while keeping the analysis quick to rerun on a normal laptop.

## Our work in this project

We designed the restaurant-delivery version of the graph model and wrote the rules for customer assignment, route calculation, road-use counting and road closure. We added the comparison between random and highest-use closures, repeated random runs, restaurant reassignment, the tied-road experiment and the road-distance seed check. We also wrote automated tests and saved every final table and figure so the report can be reproduced.

## Main findings

Highest-use closures produced a larger average distance increase than the random mean at every tested closure level under restaurant reassignment.

At four closed roads:

- Random closures increased average distance by **8.96%** on average.
- The selected highest-use closure increased it by **105.26%**.
- All customers could still reach at least one restaurant when reassignment was allowed.
- With fixed assignments, only **46.67%** of orders remained serviceable because one restaurant was isolated.

The fourth selected road was part of an eight-way usage tie. Trying every tied choice gave fixed-assignment distance increases from **56.58% to 79.41%**. Only one choice isolated the restaurant. This means the general distance effect was strong, but the exact accessibility result depended on the tie decision.

Across ten different road-distance seeds, the four-road highest-use strategy caused a larger distance increase than the random mean in every case. This does not prove the result for every city, but it shows that it was not limited to one set of weights.

## Repository structure

- `src/model.py` - creates the network and delivery routes
- `src/experiments.py` - repeated random and tie experiments
- `src/run_analysis.py` - runs the complete analysis and saves outputs
- `notebooks/final_analysis.ipynb` - readable walkthrough of the study
- `results/` - saved CSV tables
- `figures/` - saved graphs and network diagrams
- `tests/` - automated checks for the main functions

## Run the project

From the main project folder:

```bash
python -m venv .venv
```

Activate the environment, then install the packages:

```bash
python -m pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest
```

Reproduce every result and figure:

```bash
python -m src.run_analysis
```

You can also open `notebooks/final_analysis.ipynb` in Jupyter and run its cells in order.

## Limitations

This is a controlled synthetic network, not a map of a real city. It assumes two-way roads, fixed road distances and shortest-path driver behaviour. It does not include live traffic, delivery capacity, changing demand or interaction between drivers. The conclusions therefore describe this model and should not be treated as exact predictions for a real delivery company.

Repository: https://github.com/naveenswa/CITS4403-Urban-Delivery-Network
