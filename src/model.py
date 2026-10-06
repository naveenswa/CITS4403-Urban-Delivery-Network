from collections import Counter

import random

import networkx as nx


def create_road_network(rows=6, columns=6, seed=42):
    random_generator = random.Random(seed)

    road_network = nx.grid_2d_graph(rows, columns)

    for first_node, second_node in road_network.edges:
        road_network.edges[first_node, second_node]["distance"] = (
            random_generator.randint(1, 5)
        )

    return road_network

def get_delivery_locations():
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

def calculate_delivery_routes(
    road_network,
    customer_restaurants,
    weight="distance"
):
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

    return (
        delivery_routes,
        delivery_distances,
        unreachable_customers
    )

def count_road_usage(delivery_routes):
    road_usage = Counter()

    for route in delivery_routes.values():
        for position in range(len(route) - 1):
            first_node = route[position]
            second_node = route[position + 1]

            road = tuple(sorted([
                first_node,
                second_node
            ]))

            road_usage[road] += 1

    return road_usage

def select_random_roads(
    road_network,
    number_of_closures,
    seed
):
    random_generator = random.Random(seed)

    random_closed_roads = random_generator.sample(
        list(road_network.edges),
        number_of_closures
    )

    return random_closed_roads


def select_high_use_roads(
    road_usage,
    number_of_closures
):
    highest_use_roads = []

    for road, usage_count in road_usage.most_common(
        number_of_closures
    ):
        highest_use_roads.append(road)

    return highest_use_roads


def close_roads(
    road_network,
    roads_to_close
):
    closed_network = road_network.copy()
    closed_network.remove_edges_from(roads_to_close)

    return closed_network
