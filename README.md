# Urban Delivery Network Under Road Closures and Congestion

## Proposed System

This project will model a simplified urban road network used for restaurant deliveries.

Restaurants, customers and intersections will be represented as nodes. Roads will be represented as weighted edges, with each weight representing road distance.

## Motivation

Road closures can increase delivery distances or make customers unreachable. The effect may depend on whether randomly selected roads or frequently used roads are closed.

Traffic congestion can also affect deliveries without completely closing a road. A congested road remains available, but its higher travel cost may cause longer delivery times or make another route more suitable.

## Research Question

How do random road closures, closures of frequently used roads and traffic congestion affect delivery distance, travel cost and the percentage of customers remaining reachable in a simplified urban road network?

## Hypothesis

Closures of frequently used roads are expected to cause a greater increase in average delivery distance and a larger reduction in customer accessibility than random road closures.

Traffic congestion is expected to increase delivery travel cost and may cause some deliveries to use alternative routes. However, congestion alone is not expected to make customers unreachable because congested roads remain open.

## Modelling Approach

The project will use a weighted, undirected graph implemented in Python using NetworkX and Jupyter Notebook.

- Nodes: restaurants, customers and intersections
- Edges: roads
- Distance: physical road distance
- Congestion multiplier: increased cost caused by congestion
- Routes: lowest-cost available paths

For the congestion experiment, travel cost will be calculated as:

`travel cost = road distance × congestion multiplier`

The initial model assumes that roads can be travelled in both directions, road distances remain fixed, and drivers use the lowest-cost available route.

The project will not simulate how traffic jams form. Congestion will be represented as an increased travel cost on selected roads.

## Proposed Experiment

1. Create a synthetic connected road network.
2. Select restaurant and customer nodes.
3. Assign each customer to the nearest restaurant.
4. Calculate the baseline shortest delivery routes.
5. Count how many baseline routes use each road.
6. Rank roads according to their usage.
7. Close roads randomly and recalculate the routes.
8. Restore the original network.
9. Close the same number of highest-use roads.
10. Recalculate the routes and compare the results.
11. Restore the original network again.
12. Apply congestion to selected roads by increasing their travel cost without closing them.
13. Recalculate the lowest-cost delivery routes.
14. Compare the congestion results with the baseline and closure results.
15. Repeat the random experiments using multiple random seeds.

## Measurements

- Average delivery-distance increase
- Average travel-cost increase under congestion
- Percentage of customers remaining reachable
- Number of delivery routes that change
- Average and variation across repeated random experiments

## Qualitative Analysis

Network diagrams will show normal delivery routes, randomly closed roads, closed frequently used roads, congested roads, alternative routes and disconnected customers.

## Possible Extension

If the core model works, the project may compare random road repair with repairing the highest-use closed roads first.

## Initial Limitations

- The initial network will be synthetic.
- All roads will be treated as two-way.
- Congestion will be represented using a simplified travel-cost multiplier rather than a dynamic traffic-flow simulation.
- Weather and individual driver behaviour will not initially be included.
- Drivers will always use the lowest-cost available route.


