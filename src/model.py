from collections import Counter
import random

import networkx as nx


def create_road_network(rows=6, columns=6, seed=42):
    """Create a weighted grid road network with reproducible distances."""
    random_generator = random.Random(seed)
    road_network = nx.grid_2d_graph(rows, columns)

    for first_node, second_node in road_network.edges:
        road_network.edges[first_node, second_node]["distance"] = (
            random_generator.randint(1, 5)
        )

    return road_network


def get_delivery_locations():
    """Return the fixed restaurant and customer locations used in the study."""
    restaurants = [
        (0, 0),
        (5, 5),
        (0, 5)
    ]

    customers = [
        (0, 2),
        (0, 4),
        (1, 1),
        (1, 3),
        (1, 4),
        (2, 0),
        (2, 2),
        (2, 5),
        (3, 0),
        (3, 3),
        (4, 1),
        (4, 2),
        (4, 4),
        (5, 2),
        (5, 4)
    ]

    return restaurants, customers


def assign_customers_to_restaurants(
    road_network,
    restaurants,
    customers
):
    """Assign every customer to its nearest restaurant before disruption."""
    customer_restaurants = {}

    for customer in customers:
        restaurant_distances = {}

        for restaurant in restaurants:
            distance = nx.shortest_path_length(
                road_network,
                restaurant,
                customer,
                weight="distance"
            )
            restaurant_distances[restaurant] = distance

        nearest_restaurant = min(
            restaurant_distances,
            key=restaurant_distances.get
        )
        customer_restaurants[customer] = nearest_restaurant

    return customer_restaurants


def calculate_delivery_routes(
    road_network,
    customer_restaurants,
    weight="distance"
):
    """Calculate shortest routes and list customers with no available path."""
    delivery_routes = {}
    delivery_distances = {}
    unreachable_customers = []

    for customer, restaurant in customer_restaurants.items():
        try:
            delivery_routes[customer] = nx.shortest_path(
                road_network,
                restaurant,
                customer,
                weight=weight
            )
            delivery_distances[customer] = nx.shortest_path_length(
                road_network,
                restaurant,
                customer,
                weight=weight
            )
        except nx.NetworkXNoPath:
            unreachable_customers.append(customer)

    return delivery_routes, delivery_distances, unreachable_customers


def count_road_usage(delivery_routes):
    """Count how many baseline delivery routes contain each road."""
    road_usage = Counter()

    for route in delivery_routes.values():
        for position in range(len(route) - 1):
            first_node = route[position]
            second_node = route[position + 1]
            road = tuple(sorted([first_node, second_node]))
            road_usage[road] += 1

    return road_usage


def select_random_roads(road_network, number_of_closures, seed):
    """Select distinct roads using a reproducible random seed."""
    if number_of_closures < 0:
        raise ValueError("number_of_closures cannot be negative")

    if number_of_closures > road_network.number_of_edges():
        raise ValueError("number_of_closures exceeds the number of roads")

    random_generator = random.Random(seed)

    return random_generator.sample(
        list(road_network.edges),
        number_of_closures
    )


def select_high_use_roads(road_usage, number_of_closures):
    """Rank roads by usage, then by road coordinates to resolve ties."""
    ranked_roads = sorted(
        road_usage.items(),
        key=lambda item: (-item[1], item[0])
    )

    return [
        road
        for road, usage_count in ranked_roads[:number_of_closures]
    ]


def get_tied_roads_at_rank(road_usage, rank):
    """Return every road tied at a one-based position in the usage ranking."""
    if rank < 1 or rank > len(road_usage):
        raise ValueError("rank must refer to a road in road_usage")

    ranked_counts = sorted(road_usage.values(), reverse=True)
    cutoff_usage = ranked_counts[rank - 1]

    return sorted([
        road
        for road, usage_count in road_usage.items()
        if usage_count == cutoff_usage
    ])


def close_roads(road_network, roads_to_close):
    """Return a copied network with the selected roads removed."""
    closed_network = road_network.copy()
    closed_network.remove_edges_from(roads_to_close)

    return closed_network


def calculate_scenario_results(
    baseline_distances,
    scenario_distances,
    total_customers
):
    """Compare scenario distances with the same customers at baseline."""
    reachable_count = len(scenario_distances)
    unreachable_count = total_customers - reachable_count
    reachable_percentage = (reachable_count / total_customers) * 100

    if reachable_count == 0:
        return {
            "average_distance": None,
            "average_distance_increase": None,
            "distance_increase_percentage": None,
            "reachable_percentage": 0,
            "unreachable_count": unreachable_count
        }

    average_scenario_distance = (
        sum(scenario_distances.values()) / reachable_count
    )

    comparable_baseline_distances = []

    for customer in scenario_distances:
        comparable_baseline_distances.append(
            baseline_distances[customer]
        )

    average_comparable_baseline = (
        sum(comparable_baseline_distances) / reachable_count
    )
    average_distance_increase = (
        average_scenario_distance - average_comparable_baseline
    )
    distance_increase_percentage = (
        average_distance_increase / average_comparable_baseline
    ) * 100

    return {
        "average_distance": average_scenario_distance,
        "average_distance_increase": average_distance_increase,
        "distance_increase_percentage": distance_increase_percentage,
        "reachable_percentage": reachable_percentage,
        "unreachable_count": unreachable_count
    }


def reassign_customers_to_available_restaurants(
    road_network,
    restaurants,
    customers,
    weight="distance"
):
    """Assign each customer to the nearest restaurant that still has a path."""
    new_assignments = {}
    unreachable_customers = []

    for customer in customers:
        available_restaurants = []

        for restaurant in restaurants:
            try:
                distance = nx.shortest_path_length(
                    road_network,
                    restaurant,
                    customer,
                    weight=weight
                )
                available_restaurants.append((distance, restaurant))
            except nx.NetworkXNoPath:
                continue

        if available_restaurants:
            distance, nearest_restaurant = min(available_restaurants)
            new_assignments[customer] = nearest_restaurant
        else:
            unreachable_customers.append(customer)

    return new_assignments, unreachable_customers


def apply_travel_cost_multiplier(
    road_network,
    adjusted_roads,
    cost_multiplier
):
    """Increase static edge costs while keeping every road open."""
    travel_cost_network = road_network.copy()

    for first_node, second_node in travel_cost_network.edges:
        normal_distance = travel_cost_network.edges[
            first_node,
            second_node
        ]["distance"]
        travel_cost_network.edges[
            first_node,
            second_node
        ]["travel_cost"] = normal_distance

    for road in adjusted_roads:
        normal_distance = travel_cost_network.edges[road]["distance"]
        travel_cost_network.edges[road]["travel_cost"] = (
            normal_distance * cost_multiplier
        )

    return travel_cost_network
