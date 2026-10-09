from src.experiments import (
    evaluate_tie_choices,
    repeat_random_closures,
    repeat_random_closures_with_reassignment,
    summarise_random_results
)
from src.model import (
    assign_customers_to_restaurants,
    calculate_delivery_routes,
    count_road_usage,
    create_road_network,
    get_delivery_locations
)


def create_baseline():
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

    return (
        road_network,
        customer_restaurants,
        baseline_distances
    )


def test_repeated_random_closures():
    road_network, customer_restaurants, baseline_distances = (
        create_baseline()
    )

    results = repeat_random_closures(
        road_network,
        customer_restaurants,
        baseline_distances,
        number_of_closures=3,
        repetitions=10
    )

    assert len(results) == 10

    for result in results:
        assert len(result["closed_roads"]) == 3
        assert 0 <= result["reachable_percentage"] <= 100

    summary = summarise_random_results(results)

    assert summary["mean_distance_increase_percentage"] >= 0
    assert 0 <= summary["mean_reachable_percentage"] <= 100
    assert summary["distance_increase_standard_deviation"] >= 0


def test_random_results_are_reproducible():
    road_network, customer_restaurants, baseline_distances = (
        create_baseline()
    )

    first_results = repeat_random_closures(
        road_network,
        customer_restaurants,
        baseline_distances,
        number_of_closures=3,
        repetitions=5
    )

    second_results = repeat_random_closures(
        road_network,
        customer_restaurants,
        baseline_distances,
        number_of_closures=3,
        repetitions=5
    )

    assert first_results == second_results


def test_reassignment_keeps_customers_serviceable_in_main_four_road_case():
    road_network, customer_restaurants, baseline_distances = (
        create_baseline()
    )
    restaurants, customers = get_delivery_locations()

    results = repeat_random_closures_with_reassignment(
        road_network,
        restaurants,
        customers,
        baseline_distances,
        number_of_closures=4,
        repetitions=5
    )

    assert len(results) == 5
    assert all(result["reachable_percentage"] == 100 for result in results)


def test_fourth_position_tie_has_eight_possible_choices():
    road_network, customer_restaurants, baseline_distances = (
        create_baseline()
    )
    routes, distances, unreachable = calculate_delivery_routes(
        road_network,
        customer_restaurants
    )
    road_usage = count_road_usage(routes)

    tie_results = evaluate_tie_choices(
        road_network,
        road_usage,
        customer_restaurants,
        baseline_distances,
        number_of_closures=4
    )

    assert len(tie_results) == 8
    assert min(
        result["reachable_percentage"]
        for result in tie_results
    ) == 46.666666666666664
    assert max(
        result["reachable_percentage"]
        for result in tie_results
    ) == 100
