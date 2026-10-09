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
    apply_travel_cost_multiplier,
    get_tied_roads_at_rank,
    reassign_customers_to_available_restaurants
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


def test_static_travel_cost_multiplier():
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
    adjusted_roads = select_high_use_roads(road_usage, 3)

    travel_cost_network = apply_travel_cost_multiplier(
        road_network,
        adjusted_roads,
        cost_multiplier=2
    )

    for road in adjusted_roads:
        assert (
            travel_cost_network.edges[road]["travel_cost"]
            == road_network.edges[road]["distance"] * 2
        )


def test_high_use_ties_are_resolved_by_road_coordinates():
    road_usage = {
        ((1, 0), (1, 1)): 4,
        ((0, 0), (1, 0)): 4,
        ((0, 0), (0, 1)): 2
    }

    selected = select_high_use_roads(road_usage, 2)

    assert selected == [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1))
    ]
    assert get_tied_roads_at_rank(road_usage, 1) == [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 1))
    ]


def test_customer_can_change_restaurant_after_isolation():
    road_network = nx.path_graph(4)

    for first_node, second_node in road_network.edges:
        road_network.edges[first_node, second_node]["distance"] = 1

    isolated_network = close_roads(road_network, [(0, 1)])
    assignments, unreachable = (
        reassign_customers_to_available_restaurants(
            isolated_network,
            restaurants=[0, 3],
            customers=[1]
        )
    )

    assert assignments[1] == 3
    assert unreachable == []


def test_zero_and_all_road_closures():
    road_network = nx.path_graph(3)

    for first_node, second_node in road_network.edges:
        road_network.edges[first_node, second_node]["distance"] = 1

    unchanged_network = close_roads(road_network, [])
    fully_closed_network = close_roads(
        road_network,
        list(road_network.edges)
    )

    assert unchanged_network.number_of_edges() == 2
    assert fully_closed_network.number_of_edges() == 0

    routes, distances, unreachable = calculate_delivery_routes(
        fully_closed_network,
        {2: 0}
    )

    assert routes == {}
    assert distances == {}
    assert unreachable == [2]


def test_hand_calculated_three_node_route():
    road_network = nx.Graph()
    road_network.add_edge("R", "A", distance=2)
    road_network.add_edge("A", "C", distance=3)
    road_network.add_edge("R", "C", distance=8)

    routes, distances, unreachable = calculate_delivery_routes(
        road_network,
        {"C": "R"}
    )

    assert routes["C"] == ["R", "A", "C"]
    assert distances["C"] == 5
    assert unreachable == []
