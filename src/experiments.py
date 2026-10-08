from statistics import mean, stdev

from src.model import (
    calculate_delivery_routes,
    calculate_scenario_results,
    close_roads,
    select_random_roads
)


def repeat_random_closures(
    road_network,
    customer_restaurants,
    baseline_distances,
    number_of_closures,
    repetitions=100
):
    experiment_results = []

    for seed in range(repetitions):
        closed_roads = select_random_roads(
            road_network,
            number_of_closures,
            seed
        )

        random_network = close_roads(
            road_network,
            closed_roads
        )

        routes, distances, unreachable = calculate_delivery_routes(
            random_network,
            customer_restaurants
        )

        results = calculate_scenario_results(
            baseline_distances,
            distances,
            len(customer_restaurants)
        )

        results["seed"] = seed
        results["number_of_closures"] = number_of_closures
        results["closed_roads"] = closed_roads
        experiment_results.append(results)

    return experiment_results


def summarise_random_results(experiment_results):
    distance_increases = []
    reachable_percentages = []

    for result in experiment_results:
        if result["distance_increase_percentage"] is not None:
            distance_increases.append(
                result["distance_increase_percentage"]
            )

        reachable_percentages.append(
            result["reachable_percentage"]
        )

    summary = {
        "mean_distance_increase_percentage": mean(distance_increases),
        "mean_reachable_percentage": mean(reachable_percentages),
        "minimum_reachable_percentage": min(reachable_percentages),
        "maximum_reachable_percentage": max(reachable_percentages)
    }

    if len(distance_increases) > 1:
        summary["distance_increase_standard_deviation"] = stdev(
            distance_increases
        )
    else:
        summary["distance_increase_standard_deviation"] = 0

    if len(reachable_percentages) > 1:
        summary["reachable_percentage_standard_deviation"] = stdev(
            reachable_percentages
        )
    else:
        summary["reachable_percentage_standard_deviation"] = 0

    return summary
