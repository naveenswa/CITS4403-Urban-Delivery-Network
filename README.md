# Urban Delivery Network Under Road Closures

## Project Overview

This project models restaurant deliveries on a simplified urban road network. The aim is to compare the effect of random road closures with closures of roads used by many delivery routes.

## Research Question

How do random road closures and closures of frequently used roads affect average delivery distance and the percentage of customers remaining reachable?

## Hypothesis

Closing frequently used roads will cause more disruption than closing the same number of randomly selected roads.

## Model

The model uses a weighted undirected graph created with Python and NetworkX.

- 36 nodes arranged as a 6 x 6 road network
- 60 roads
- 3 restaurant locations
- 15 customer locations
- Road distances between 1 and 5 units
- Fixed random seeds for reproducibility

Intersections, restaurants and customers are nodes. Roads are edges, and distance is the edge weight.

Each customer is assigned to the restaurant with the shortest weighted distance. Drivers then use the shortest available route.

## Road Usage

The baseline delivery routes are calculated before any disruption. Road usage is found by counting how many baseline routes contain each road. Roads with the highest counts are treated as the highest se roads.

## Closure Experiments

The model compares random closures and highest-use road closures at these levels:

- 1, 2, 3, 4, 5, 6, 8 and 10 roads

Random closures are repeated 100 times using different seeds. The model records:

- Average delivery-distance increase
- Standard deviation across random runs
- Percentage of customers remaining reachable
- Number of unreachable customers

Unreachable customers are reported separately and are not included in the average distance calculation.

## Traffic Congestion Case

A separate test applies congestion to the three highest-use roads. Congestion increases travel cost but does not close the road. Drivers can change routes when another route has a lower total cost.

This is a simplified travel-cost measure and does not represent exact delivery time.

## Main Results

Highest use road closures caused a larger distance increase than random closures at every closure level in the main experiment.

With one road closed, the distance increase was 18.42% for the highest-use closure and 3.53% for the random average.

When four highest use roads were closed, customer reachability dropped to 46.67%. The random experiments still had an average reachability of 100% at the same closure level.

At a congestion multiplier of 3.0, travel cost increased by 23.68%, four delivery routes changed, and all customers remained reachable.

## Sensitivity Test

The four road comparison was repeated using ten different road-distance seeds. Highest-use closures caused a larger distance increase than random closures in all ten tests.

Highest use closures reduced customer reachability in two of the ten seeds. This shows that the distance result was consistent, while disconnection depended more on the specific road weights and route structure.

## Repository Structure

- `src/model.py` — road network and delivery model
- `src/experiments.py` — repeated random experiments
- `notebooks/final_analysis.ipynb` — complete analysis
- `results/` — experiment results in CSV format
- `figures/` — graphs and network diagrams
- `tests/` — automated tests

## Running the Project

Open `notebooks/final_analysis.ipynb` in Google Colab and run the cells in order. When prompted, upload `src/model.py` and `src/experiments.py`.

The automated tests can also be run with:

```bash
python -m pytest
