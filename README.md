# Urban Delivery Network Under Road Closures

## Proposed System

This project will model a simplified urban road network used for restaurant deliveries.

Restaurants, customers and intersections will be represented as nodes. Roads will be represented as weighted edges, with each weight representing road distance.

## Motivation

Road closures can increase delivery distances or make customers unreachable. The effect may depend on whether randomly selected roads or frequently used roads are closed.

## Research Question

How do random road closures and closures of frequently used roads affect average delivery distance and the percentage of customers remaining reachable in a simplified urban road network?

## Hypothesis

Closures of frequently used roads are expected to cause a greater increase in average delivery distance and a larger reduction in customer accessibility than random road closures.

## Modelling Approach

The project will use a weighted, undirected graph implemented in Python using NetworkX and Jupyter Notebook.

- Nodes: restaurants, customers and intersections
- Edges: roads
- Edge weights: road distances
- Routes: shortest weighted paths

The initial model assumes that roads can be travelled in both directions, road distances remain fixed, and drivers always use the shortest available route.

## Proposed Experiment

1. Create a synthetic connected road network.
2. Select restaurant and customer nodes.
3. Assign each customer to the nearest restaurant.
4. Calculate baseline shortest delivery routes.
5. Count how many baseline routes use each road.
6. Rank roads according to their usage.
7. Close roads randomly and recalculate the routes.
8. Restore the original network.
9. Close the same number of highest-use roads.
10. Recalculate the routes and compare the results.
11. Repeat the random experiments using multiple random seeds.

## Measurements

- Average delivery-distance increase
- Percentage of customers remaining reachable
- Average and variation across repeated random experiments

## Qualitative Analysis

Network diagrams will show normal delivery routes, closed roads, detours and disconnected customers.

## Possible Extension

If the core model works, the project may compare random road repair with repairing the highest-use closed roads first.

## Initial Limitations

- The initial network will be synthetic.
- All roads will be treated as two-way.
- Traffic, weather and changing travel times will not be included.
- Drivers will always use the shortest available route.

## Questions for the Facilitator

1. Is the research question sufficiently focused?
2. Is a synthetic road network appropriate?
3. Should repair strategies be included in the main investigation or treated as an extension?
