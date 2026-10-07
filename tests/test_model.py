import networkx as nx

from src.model import (
    create_road_network,
    get_delivery_locations,
    assign_customers_to_restaurants,
    calculate_delivery_routes,
    count_road_usage,
    select_random_roads,
    select_high_use_roads,
    close_roads,
    calculate_scenario_results,
    apply_congestion
)


def test_baseline_model():
    road_network = create_road_network()
    restaurants, customers = get_delivery_locations()

    assert road_network.number_of_nodes() == 36
    assert road_network.number_of_edges() == 60
    assert nx.is_connected(road_network)

    assert len(restaurants) == 3
    assert len(customers) == 15

    customer_restaurants = assign_customers_to_restaurants(
        road_network,
        restaurants,
        customers
    )

    routes, distances, unreachable = calculate_delivery_routes(
        road_network,
        customer_restaurants
    )

    assert len(customer_restaurants) == 15
    assert len(routes) == 15
    assert len(distances) == 15
    assert len(unreachable) == 0

    road_usage = count_road_usage(routes)

    assert len(road_usage) > 0


def test_road_closures():
    road_network = create_road_network()
    restaurants, customers = get_delivery_locations()

    customer_restaurants = assign_customers_to_restaurants(
        road_network,
        restaurants,
        customers
    )

    routes, baseline_distances, unreachable = (
        calculate_delivery_routes(
            road_network,
            customer_restaurants
        )
    )

    road_usage = count_road_usage(routes)

    random_roads = select_random_roads(
        road_network,
        number_of_closures=3,
        seed=10
    )

    high_use_roads = select_high_use_roads(
        road_usage,
        number_of_closures=3
    )

    random_network = close_roads(
        road_network,
        random_roads
    )

    high_use_network = close_roads(
        road_network,
        high_use_roads
    )

    assert random_network.number_of_edges() == 57
    assert high_use_network.number_of_edges() == 57

    for road in random_roads:
        assert not random_network.has_edge(*road)
        assert road_network.has_edge(*road)


def test_baseline_results():
    road_network = create_road_network()
    restaurants, customers = get_delivery_locations()

    customer_restaurants = assign_customers_to_restaurants(
        road_network,
        restaurants,
        customers
    )

    routes, baseline_distances, unreachable = (
        calculate_delivery_routes(
            road_network,
            customer_restaurants
        )
    )

    results = calculate_scenario_results(
        baseline_distances,
        baseline_distances,
        len(customers)
    )

    assert results["average_distance_increase"] == 0
    assert results["distance_increase_percentage"] == 0
    assert results["reachable_percentage"] == 100


def test_congestion():
    road_network = create_road_network()
    restaurants, customers = get_delivery_locations()

    customer_restaurants = assign_customers_to_restaurants(
        road_network,
        restaurants,
        customers
    )

    routes, distances, unreachable = calculate_delivery_routes(
        road_network,
        customer_restaurants
    )

    road_usage = count_road_usage(routes)
    congested_roads = select_high_use_roads(road_usage, 3)

    congestion_network = apply_congestion(
        road_network,
        congested_roads,
        congestion_multiplier=2
    )

    for road in congested_roads:
        assert (
            congestion_network.edges[road]["travel_cost"]
            == road_network.edges[road]["distance"] * 2
        )
