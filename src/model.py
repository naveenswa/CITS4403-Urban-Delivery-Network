            )
        except nx.NetworkXNoPath:
            unreachable_customers.append(customer)

    return delivery_routes, delivery_distances, unreachable_customers


def count_road_usage(delivery_routes):
    road_usage = Counter()

    for route in delivery_routes.values():
        for position in range(len(route) - 1):
            first_node = route[position]
            second_node = route[position + 1]
            road = tuple(sorted([first_node, second_node]))
            road_usage[road] += 1

    return road_usage


def select_random_roads(road_network, number_of_closures, seed):
    random_generator = random.Random(seed)

    return random_generator.sample(
        list(road_network.edges),
        number_of_closures
    )


def select_high_use_roads(road_usage, number_of_closures):
    highest_use_roads = []

    for road, usage_count in road_usage.most_common(number_of_closures):
        highest_use_roads.append(road)

    return highest_use_roads


def close_roads(road_network, roads_to_close):
    closed_network = road_network.copy()
    closed_network.remove_edges_from(roads_to_close)

    return closed_network


def calculate_scenario_results(
    baseline_distances,
    scenario_distances,
    total_customers
):
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


def apply_congestion(
    road_network,
    congested_roads,
    congestion_multiplier
):
    congestion_network = road_network.copy()

    for first_node, second_node in congestion_network.edges:
        normal_distance = congestion_network.edges[
            first_node,
            second_node
        ]["distance"]
        congestion_network.edges[
            first_node,
            second_node
        ]["travel_cost"] = normal_distance

    for road in congested_roads:
        normal_distance = congestion_network.edges[road]["distance"]
        congestion_network.edges[road]["travel_cost"] = (
            normal_distance * congestion_multiplier
        )

    return congestion_network
