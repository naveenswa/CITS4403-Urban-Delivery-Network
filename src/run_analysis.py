"""Run the complete project analysis and save tables and figures."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import pandas as pd

from src.experiments import (
    evaluate_tie_choices,
    repeat_random_closures,
    repeat_random_closures_with_reassignment,
    summarise_random_results
)
from src.model import (
    apply_travel_cost_multiplier,
    assign_customers_to_restaurants,
    calculate_delivery_routes,
    calculate_scenario_results,
    close_roads,
    count_road_usage,
    create_road_network,
    get_delivery_locations,
    reassign_customers_to_available_restaurants,
    select_high_use_roads
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIRECTORY = PROJECT_ROOT / "results"
FIGURES_DIRECTORY = PROJECT_ROOT / "figures"


def evaluate_high_use_scenario(
    road_network,
    road_usage,
    original_assignments,
    restaurants,
    customers,
    baseline_distances,
    number_of_closures
):
    """Evaluate one explicitly ranked highest-use closure scenario."""
    closed_roads = select_high_use_roads(
        road_usage,
        number_of_closures
    )
    closed_network = close_roads(road_network, closed_roads)

    fixed_routes, fixed_distances, fixed_unreachable = (
        calculate_delivery_routes(
            closed_network,
            original_assignments
        )
    )
    fixed_results = calculate_scenario_results(
        baseline_distances,
        fixed_distances,
        len(customers)
    )

    new_assignments, no_available_restaurant = (
        reassign_customers_to_available_restaurants(
            closed_network,
            restaurants,
            customers
        )
    )
    flexible_routes, flexible_distances, flexible_unreachable = (
        calculate_delivery_routes(
            closed_network,
            new_assignments
        )
    )
    flexible_results = calculate_scenario_results(
        baseline_distances,
        flexible_distances,
        len(customers)
    )

    return {
        "closed_roads": closed_roads,
        "closed_network": closed_network,
        "fixed_routes": fixed_routes,
        "fixed_unreachable": fixed_unreachable,
        "fixed_results": fixed_results,
        "flexible_routes": flexible_routes,
        "flexible_unreachable": (
            no_available_restaurant + flexible_unreachable
        ),
        "flexible_results": flexible_results
    }


def create_closure_comparison():
    """Run the main comparison under fixed and flexible service policies."""
    road_network = create_road_network()
    restaurants, customers = get_delivery_locations()
    assignments = assign_customers_to_restaurants(
        road_network,
        restaurants,
        customers
    )
    baseline_routes, baseline_distances, baseline_unreachable = (
        calculate_delivery_routes(road_network, assignments)
    )
    road_usage = count_road_usage(baseline_routes)

    closure_levels = [1, 2, 3, 4, 5, 6, 8, 10]
    comparison_rows = []
    random_run_rows = []

    for number_of_closures in closure_levels:
        fixed_random_runs = repeat_random_closures(
            road_network,
            assignments,
            baseline_distances,
            number_of_closures,
            repetitions=100
        )
        flexible_random_runs = repeat_random_closures_with_reassignment(
            road_network,
            restaurants,
            customers,
            baseline_distances,
            number_of_closures,
            repetitions=100
        )
        fixed_summary = summarise_random_results(fixed_random_runs)
        flexible_summary = summarise_random_results(flexible_random_runs)

        high_use = evaluate_high_use_scenario(
            road_network,
            road_usage,
            assignments,
            restaurants,
            customers,
            baseline_distances,
            number_of_closures
        )
        targeted_flexible_distance = high_use[
            "flexible_results"
        ]["distance_increase_percentage"]
        random_equal_or_worse = sum(
            result["distance_increase_percentage"]
            >= targeted_flexible_distance
            for result in flexible_random_runs
        )

        comparison_rows.append({
            "roads_closed": number_of_closures,
            "random_fixed_distance_mean": fixed_summary[
                "mean_distance_increase_percentage"
            ],
            "random_fixed_reachable_mean": fixed_summary[
                "mean_reachable_percentage"
            ],
            "high_use_fixed_distance": high_use[
                "fixed_results"
            ]["distance_increase_percentage"],
            "high_use_fixed_reachable": high_use[
                "fixed_results"
            ]["reachable_percentage"],
            "random_flexible_distance_mean": flexible_summary[
                "mean_distance_increase_percentage"
            ],
            "random_flexible_distance_median": flexible_summary[
                "median_distance_increase_percentage"
            ],
            "random_flexible_distance_p10": flexible_summary[
                "distance_increase_p10"
            ],
            "random_flexible_distance_p90": flexible_summary[
                "distance_increase_p90"
            ],
            "random_flexible_reachable_mean": flexible_summary[
                "mean_reachable_percentage"
            ],
            "random_flexible_reachable_p10": flexible_summary[
                "reachable_percentage_p10"
            ],
            "random_flexible_reachable_p90": flexible_summary[
                "reachable_percentage_p90"
            ],
            "high_use_flexible_distance": targeted_flexible_distance,
            "high_use_flexible_reachable": high_use[
                "flexible_results"
            ]["reachable_percentage"],
            "random_runs_equal_or_worse_percent": (
                random_equal_or_worse / len(flexible_random_runs) * 100
            )
        })

        for result in flexible_random_runs:
            random_run_rows.append({
                "roads_closed": number_of_closures,
                "seed": result["seed"],
                "distance_increase_percentage": result[
                    "distance_increase_percentage"
                ],
                "reachable_percentage": result[
                    "reachable_percentage"
                ]
            })

    comparison_table = pd.DataFrame(comparison_rows)
    random_runs_table = pd.DataFrame(random_run_rows)

    return {
        "road_network": road_network,
        "restaurants": restaurants,
        "customers": customers,
        "assignments": assignments,
        "baseline_routes": baseline_routes,
        "baseline_distances": baseline_distances,
        "baseline_unreachable": baseline_unreachable,
        "road_usage": road_usage,
        "comparison_table": comparison_table,
        "random_runs_table": random_runs_table
    }


def create_tie_sensitivity(main_results):
    """Test every road tied for the fourth highest-use closure position."""
    tie_results = evaluate_tie_choices(
        main_results["road_network"],
        main_results["road_usage"],
        main_results["assignments"],
        main_results["baseline_distances"],
        number_of_closures=4
    )
    rows = []

    for choice_number, result in enumerate(tie_results, start=1):
        closed_network = close_roads(
            main_results["road_network"],
            result["closed_roads"]
        )
        new_assignments, no_restaurant = (
            reassign_customers_to_available_restaurants(
                closed_network,
                main_results["restaurants"],
                main_results["customers"]
            )
        )
        routes, distances, no_path = calculate_delivery_routes(
            closed_network,
            new_assignments
        )
        flexible_results = calculate_scenario_results(
            main_results["baseline_distances"],
            distances,
            len(main_results["customers"])
        )

        rows.append({
            "choice": choice_number,
            "tied_road": str(result["tied_choice"][0]),
            "fixed_distance_increase": result[
                "distance_increase_percentage"
            ],
            "fixed_reachable_percentage": result[
                "reachable_percentage"
            ],
            "flexible_distance_increase": flexible_results[
                "distance_increase_percentage"
            ],
            "flexible_reachable_percentage": flexible_results[
                "reachable_percentage"
            ]
        })

    return pd.DataFrame(rows)


def create_travel_cost_results(main_results):
    """Run the optional static edge-cost sensitivity check."""
    adjusted_roads = select_high_use_roads(
        main_results["road_usage"],
        3
    )
    cost_multipliers = [1.0, 1.25, 1.5, 2.0, 3.0]
    rows = []

    for multiplier in cost_multipliers:
        adjusted_network = apply_travel_cost_multiplier(
            main_results["road_network"],
            adjusted_roads,
            multiplier
        )
        routes, distances, unreachable = calculate_delivery_routes(
            adjusted_network,
            main_results["assignments"],
            weight="travel_cost"
        )
        results = calculate_scenario_results(
            main_results["baseline_distances"],
            distances,
            len(main_results["customers"])
        )
        changed_routes = sum(
            routes[customer] != main_results["baseline_routes"][customer]
            for customer in main_results["customers"]
        )
        rows.append({
            "cost_multiplier": multiplier,
            "travel_cost_increase": results[
                "distance_increase_percentage"
            ],
            "routes_changed": changed_routes,
            "customers_reachable": results["reachable_percentage"]
        })

    return pd.DataFrame(rows)


def create_seed_sensitivity():
    """Repeat the four-road flexible-policy comparison across ten seeds."""
    rows = []

    for network_seed in range(10):
        road_network = create_road_network(seed=network_seed)
        restaurants, customers = get_delivery_locations()
        assignments = assign_customers_to_restaurants(
            road_network,
            restaurants,
            customers
        )
        routes, baseline_distances, unreachable = calculate_delivery_routes(
            road_network,
            assignments
        )
        road_usage = count_road_usage(routes)

        random_runs = repeat_random_closures_with_reassignment(
            road_network,
            restaurants,
            customers,
            baseline_distances,
            number_of_closures=4,
            repetitions=50
        )
        random_summary = summarise_random_results(random_runs)
        high_use = evaluate_high_use_scenario(
            road_network,
            road_usage,
            assignments,
            restaurants,
            customers,
            baseline_distances,
            number_of_closures=4
        )

        rows.append({
            "network_seed": network_seed,
            "random_flexible_distance_mean": random_summary[
                "mean_distance_increase_percentage"
            ],
            "high_use_flexible_distance": high_use[
                "flexible_results"
            ]["distance_increase_percentage"],
            "random_flexible_reachable_mean": random_summary[
                "mean_reachable_percentage"
            ],
            "high_use_flexible_reachable": high_use[
                "flexible_results"
            ]["reachable_percentage"]
        })

    return pd.DataFrame(rows)


def save_main_figures(main_results, tie_table, seed_table, cost_table):
    """Create the final figures used by the notebook and report."""
    table = main_results["comparison_table"]
    x = table["roads_closed"]

    plt.figure(figsize=(9, 5))
    plt.fill_between(
        x,
        table["random_flexible_distance_p10"],
        table["random_flexible_distance_p90"],
        alpha=0.2,
        color="tab:blue",
        label="Random 10th–90th percentile"
    )
    plt.plot(
        x,
        table["random_flexible_distance_mean"],
        marker="o",
        color="tab:blue",
        label="Random mean"
    )
    plt.plot(
        x,
        table["high_use_flexible_distance"],
        marker="s",
        color="tab:orange",
        label="Highest-use ranking"
    )
    plt.xlabel("Number of roads closed")
    plt.ylabel("Average delivery distance increase (%)")
    plt.title("Delivery Distance with Restaurant Reassignment")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "distance_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    figure, graphs = plt.subplots(1, 2, figsize=(12, 4.5))
    graphs[0].plot(
        x,
        table["random_fixed_reachable_mean"],
        marker="o",
        label="Random mean"
    )
    graphs[0].plot(
        x,
        table["high_use_fixed_reachable"],
        marker="s",
        label="Highest-use ranking"
    )
    graphs[0].set_title("Fixed Restaurant Assignments")
    graphs[0].set_xlabel("Number of roads closed")
    graphs[0].set_ylabel("Orders still serviceable (%)")
    graphs[0].set_ylim(0, 105)
    graphs[0].grid(alpha=0.3)
    graphs[0].legend()

    graphs[1].plot(
        x,
        table["random_flexible_reachable_mean"],
        marker="o",
        label="Random mean"
    )
    graphs[1].plot(
        x,
        table["high_use_flexible_reachable"],
        marker="s",
        label="Highest-use ranking"
    )
    graphs[1].set_title("Restaurant Reassignment Allowed")
    graphs[1].set_xlabel("Number of roads closed")
    graphs[1].set_ylabel("Customers reachable (%)")
    graphs[1].set_ylim(0, 105)
    graphs[1].grid(alpha=0.3)
    graphs[1].legend()
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "reachability_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    figure, graphs = plt.subplots(1, 2, figsize=(12, 4.5))
    labels = [f"Choice {value}" for value in tie_table["choice"]]
    graphs[0].bar(
        labels,
        tie_table["fixed_distance_increase"],
        color="tab:orange"
    )
    graphs[0].set_ylabel("Distance increase (%)")
    graphs[0].set_title("Distance Under Each Fourth-Road Tie Choice")
    graphs[0].tick_params(axis="x", rotation=45)
    graphs[0].grid(axis="y", alpha=0.3)

    graphs[1].scatter(
        labels,
        tie_table["fixed_reachable_percentage"],
        color="tab:blue",
        s=55
    )
    graphs[1].set_ylabel("Fixed-assignment serviceability (%)")
    graphs[1].set_ylim(0, 105)
    graphs[1].set_title("Serviceability Under Each Tie Choice")
    graphs[1].tick_params(axis="x", rotation=45)
    graphs[1].grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "tie_sensitivity.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    figure, graphs = plt.subplots(1, 2, figsize=(12, 4.5))
    graphs[0].scatter(
        seed_table["network_seed"],
        seed_table["random_flexible_distance_mean"],
        label="Random mean"
    )
    graphs[0].scatter(
        seed_table["network_seed"],
        seed_table["high_use_flexible_distance"],
        marker="s",
        label="Highest-use ranking"
    )
    graphs[0].set_xlabel("Road-distance seed")
    graphs[0].set_ylabel("Distance increase (%)")
    graphs[0].set_title("Four-Road Distance Result Across Seeds")
    graphs[0].grid(alpha=0.3)
    graphs[0].legend()

    graphs[1].scatter(
        seed_table["network_seed"],
        seed_table["random_flexible_reachable_mean"],
        label="Random mean"
    )
    graphs[1].scatter(
        seed_table["network_seed"],
        seed_table["high_use_flexible_reachable"],
        marker="s",
        label="Highest-use ranking"
    )
    graphs[1].set_xlabel("Road-distance seed")
    graphs[1].set_ylabel("Customers reachable (%)")
    graphs[1].set_ylim(0, 105)
    graphs[1].set_title("Four-Road Reachability Across Seeds")
    graphs[1].grid(alpha=0.3)
    graphs[1].legend()
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "network_seed_sensitivity.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    figure, graphs = plt.subplots(1, 2, figsize=(12, 4))
    graphs[0].plot(
        cost_table["cost_multiplier"],
        cost_table["travel_cost_increase"],
        marker="o",
        color="darkorange"
    )
    graphs[0].set_xlabel("Static cost multiplier")
    graphs[0].set_ylabel("Travel-cost increase (%)")
    graphs[0].set_title("Static Edge-Cost Sensitivity")
    graphs[0].grid(alpha=0.3)
    graphs[1].bar(
        cost_table["cost_multiplier"].astype(str),
        cost_table["routes_changed"],
        color="steelblue"
    )
    graphs[1].set_xlabel("Static cost multiplier")
    graphs[1].set_ylabel("Number of routes changed")
    graphs[1].set_title("Route Changes")
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "travel_cost_results.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()


def save_network_figure(main_results):
    """Show restaurant isolation and flexible reassignment after four closures."""
    high_use = evaluate_high_use_scenario(
        main_results["road_network"],
        main_results["road_usage"],
        main_results["assignments"],
        main_results["restaurants"],
        main_results["customers"],
        main_results["baseline_distances"],
        number_of_closures=4
    )
    route_roads = set()

    for route in high_use["flexible_routes"].values():
        for position in range(len(route) - 1):
            route_roads.add(tuple(sorted([
                route[position],
                route[position + 1]
            ])))

    affected_customers = set(high_use["fixed_unreachable"])
    positions = {node: node for node in main_results["road_network"].nodes}
    node_colours = []

    for node in main_results["road_network"].nodes:
        if node in main_results["restaurants"]:
            node_colours.append("red")
        elif node in affected_customers:
            node_colours.append("black")
        elif node in main_results["customers"]:
            node_colours.append("royalblue")
        else:
            node_colours.append("lightgray")

    plt.figure(figsize=(11, 8))
    nx.draw_networkx_edges(
        main_results["road_network"],
        positions,
        edge_color="lightgray",
        width=1
    )
    nx.draw_networkx_edges(
        main_results["road_network"],
        positions,
        edgelist=list(route_roads),
        edge_color="orange",
        width=2
    )
    nx.draw_networkx_edges(
        main_results["road_network"],
        positions,
        edgelist=high_use["closed_roads"],
        edge_color="red",
        width=4,
        style="dashed"
    )
    nx.draw_networkx_nodes(
        main_results["road_network"],
        positions,
        node_color=node_colours,
        node_size=350
    )

    normal_labels = {
        node: str(node)
        for node in main_results["road_network"].nodes
        if node not in affected_customers
    }
    affected_labels = {
        node: str(node)
        for node in affected_customers
    }
    nx.draw_networkx_labels(
        main_results["road_network"],
        positions,
        labels=normal_labels,
        font_size=7
    )
    nx.draw_networkx_labels(
        main_results["road_network"],
        positions,
        labels=affected_labels,
        font_size=7,
        font_color="white"
    )

    legend_items = [
        Line2D([0], [0], color="red", lw=4, ls="--", label="Closed road"),
        Line2D([0], [0], color="orange", lw=2, label="Reassigned route"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="red", markersize=9, label="Restaurant"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="royalblue", markersize=9, label="Unaffected customer"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="black", markersize=9, label="Customer losing assigned restaurant")
    ]
    plt.legend(
        handles=legend_items,
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        ncol=1,
        frameon=False
    )
    plt.title("Four Highest-Use Closures and Restaurant Reassignment")
    plt.axis("off")
    plt.tight_layout(rect=(0, 0, 0.78, 1))
    plt.savefig(
        FIGURES_DIRECTORY / "high_use_closure_network.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()


def main():
    RESULTS_DIRECTORY.mkdir(exist_ok=True)
    FIGURES_DIRECTORY.mkdir(exist_ok=True)

    main_results = create_closure_comparison()
    tie_table = create_tie_sensitivity(main_results)
    cost_table = create_travel_cost_results(main_results)
    seed_table = create_seed_sensitivity()

    main_results["comparison_table"].round(4).to_csv(
        RESULTS_DIRECTORY / "closure_comparison_results.csv",
        index=False
    )
    main_results["random_runs_table"].round(4).to_csv(
        RESULTS_DIRECTORY / "random_run_results.csv",
        index=False
    )
    tie_table.round(4).to_csv(
        RESULTS_DIRECTORY / "tie_sensitivity_results.csv",
        index=False
    )
    cost_table.round(4).to_csv(
        RESULTS_DIRECTORY / "travel_cost_results.csv",
        index=False
    )
    seed_table.round(4).to_csv(
        RESULTS_DIRECTORY / "network_seed_results.csv",
        index=False
    )

    save_main_figures(main_results, tie_table, seed_table, cost_table)
    save_network_figure(main_results)

    print("Analysis completed")
    print("Baseline average distance:", round(
        sum(main_results["baseline_distances"].values())
        / len(main_results["baseline_distances"]),
        2
    ))
    print("Results saved in:", RESULTS_DIRECTORY)
    print("Figures saved in:", FIGURES_DIRECTORY)


if __name__ == "__main__":
    main()
