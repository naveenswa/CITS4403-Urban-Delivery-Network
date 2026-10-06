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
