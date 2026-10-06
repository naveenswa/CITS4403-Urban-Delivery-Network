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
