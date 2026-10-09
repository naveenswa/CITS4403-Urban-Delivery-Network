from itertools import combinations
from statistics import mean, median, stdev

from src.model import (
    calculate_delivery_routes,
    calculate_scenario_results,
    close_roads,
    reassign_customers_to_available_restaurants,
    select_random_roads
)


def calculate_percentile(values, percentile):
    """Calculate a percentile using linear interpolation."""
    ordered_values = sorted(values)
    position = (len(ordered_values) - 1) * percentile / 100
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered_values) - 1)
    fraction = position - lower_index

    return (
        ordered_values[lower_index] * (1 - fraction)
        + ordered_values[upper_index] * fraction
    )


def repeat_random_closures(
    road_network,
    customer_restaurants,
    baseline_distances,
    number_of_closures,
    repetitions=100
):
    """Repeat fixed-assignment random closures using seeds from zero upward."""
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


def repeat_random_closures_with_reassignment(
    road_network,
    restaurants,
    customers,
    baseline_distances,
    number_of_closures,
    repetitions=100
):
    """Repeat random closures and allow customers to change restaurant."""
    experiment_results = []

    for seed in range(repetitions):
        closed_roads = select_random_roads(
            road_network,
            number_of_closures,
            seed
        )
        random_network = close_roads(road_network, closed_roads)

        assignments, no_restaurant = (
            reassign_customers_to_available_restaurants(
                random_network,
                restaurants,
                customers
            )
        )
        routes, distances, no_path = calculate_delivery_routes(
            random_network,
            assignments
        )
        results = calculate_scenario_results(
            baseline_distances,
            distances,
            len(customers)
        )
        results["seed"] = seed
        results["closed_roads"] = closed_roads
        results["unreachable_customers"] = no_restaurant + no_path
        experiment_results.append(results)

    return experiment_results


def evaluate_tie_choices(
    road_network,
    road_usage,
    customer_restaurants,
    baseline_distances,
    number_of_closures
):
    """Evaluate every valid choice when roads tie at the closure cutoff."""
    ranked_counts = sorted(road_usage.values(), reverse=True)
    cutoff_usage = ranked_counts[number_of_closures - 1]

    fixed_roads = sorted([
        road
        for road, usage_count in road_usage.items()
        if usage_count > cutoff_usage
    ])
    tied_roads = sorted([
        road
        for road, usage_count in road_usage.items()
        if usage_count == cutoff_usage
    ])
    spaces_left = number_of_closures - len(fixed_roads)
    tie_results = []

    for tied_choice in combinations(tied_roads, spaces_left):
        closed_roads = fixed_roads + list(tied_choice)
        closed_network = close_roads(road_network, closed_roads)
        routes, distances, unreachable = calculate_delivery_routes(
            closed_network,
            customer_restaurants
        )
        results = calculate_scenario_results(
            baseline_distances,
            distances,
            len(customer_restaurants)
        )
        results["closed_roads"] = closed_roads
        results["tied_choice"] = list(tied_choice)
        tie_results.append(results)

    return tie_results


def summarise_random_results(experiment_results):
    """Summarise random results using both spread and percentile ranges."""
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
        "median_distance_increase_percentage": median(distance_increases),
        "distance_increase_p10": calculate_percentile(
            distance_increases,
            10
        ),
        "distance_increase_p90": calculate_percentile(
            distance_increases,
            90
        ),
        "mean_reachable_percentage": mean(reachable_percentages),
        "reachable_percentage_p10": calculate_percentile(
            reachable_percentages,
            10
        ),
        "reachable_percentage_p90": calculate_percentile(
            reachable_percentages,
            90
        ),
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
