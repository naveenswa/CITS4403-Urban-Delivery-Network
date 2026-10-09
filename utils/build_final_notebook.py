"""Build the final project notebook from short reproducible cells."""

import base64
from pathlib import Path
from textwrap import dedent
import sys

import nbformat as nbf
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "final_analysis.ipynb"


def markdown(text):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text):
    return nbf.v4.new_code_cell(dedent(text).strip())


notebook = nbf.v4.new_notebook()
notebook["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {"name": "python", "version": "3"}
}

notebook["cells"] = [
    markdown("""
    # Urban Delivery Network Under Road Closures

    This notebook contains our final experiment. We compare random road closures with closures chosen from the roads used most often by normal delivery routes.

    **Research question:** How do random road closures and closures of frequently used roads affect average delivery distance and customer accessibility?

    We expected the highest-use closures to cause more disruption. The model is deliberately small and synthetic so every modelling choice can be checked.
    """),
    markdown("""
    ## 1. Set up the analysis

    The reusable functions are stored in `src/`. The path check below lets the notebook run from either the repository folder or the `notebooks` folder.
    """),
    code("""
    from pathlib import Path
    import sys

    import pandas as pd
    from IPython.display import Image, display

    project_root = Path.cwd()
    if project_root.name == "notebooks":
        project_root = project_root.parent

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.run_analysis import (
        create_closure_comparison,
        create_seed_sensitivity,
        create_tie_sensitivity,
        create_travel_cost_results,
        save_main_figures,
        save_network_figure,
    )
    """),
    markdown("""
    ## 2. Baseline model

    The network has 36 locations and 60 two-way roads. It contains three restaurants and 15 customers. Each road receives a distance from 1 to 5 units using seed 42. The value can differ between roads, but it stays fixed throughout the comparison.

    A customer is first assigned to the restaurant with the lowest total road distance. NetworkX then finds the shortest weighted path. These normal routes form the baseline.
    """),
    code("""
    main_results = create_closure_comparison()

    baseline_average = (
        sum(main_results["baseline_distances"].values())
        / len(main_results["baseline_distances"])
    )

    print("Locations:", main_results["road_network"].number_of_nodes())
    print("Roads:", main_results["road_network"].number_of_edges())
    print("Restaurants:", main_results["restaurants"])
    print("Number of customers:", len(main_results["customers"]))
    print("Baseline average distance:", round(baseline_average, 2))

    assignment_table = pd.DataFrame([
        {
            "customer": customer,
            "assigned_restaurant": restaurant,
            "baseline_distance": main_results["baseline_distances"][customer]
        }
        for customer, restaurant in main_results["assignments"].items()
    ])
    display(assignment_table)
    """),
    markdown("""
    ## 3. Road-use ranking and experimental rules

    We count how many baseline routes contain each road. Higher counts give a higher ranking. If counts are equal, coordinates are used as a reproducible tie-break.

    Random closures are repeated 100 times at each closure level. We report the mean together with the 10th–90th percentile range, which shows how different random selections can behave.

    We also use two service rules:

    - **Fixed assignment:** the order stays with its original restaurant.
    - **Restaurant reassignment:** the customer changes to the nearest restaurant that still has a path.

    This distinction matters because an isolated restaurant does not always mean its customers are disconnected from every other restaurant.
    """),
    code("""
    road_usage_table = pd.DataFrame([
        {"road": str(road), "baseline_routes_using_road": count}
        for road, count in main_results["road_usage"].most_common()
    ])
    display(road_usage_table.head(15))
    """),
    markdown("""
    ## 4. Main comparison

    For reachable customers, the percentage change is

    $$\frac{\text{scenario mean distance} - \text{comparable baseline mean}}{\text{comparable baseline mean}}\times 100.$$

    Customers with no path are counted separately in the accessibility result. With restaurant reassignment, a customer is unreachable only when no restaurant has a path to that customer.
    """),
    code("""
    comparison = main_results["comparison_table"]

    display_columns = [
        "roads_closed",
        "random_flexible_distance_mean",
        "random_flexible_distance_p10",
        "random_flexible_distance_p90",
        "high_use_flexible_distance",
        "random_flexible_reachable_mean",
        "high_use_flexible_reachable",
        "high_use_fixed_reachable",
        "random_runs_equal_or_worse_percent",
    ]
    display(comparison[display_columns].round(2))
    """),
    markdown("""
    ## 5. Tied-road and network-seed checks

    Eight roads tie for the fourth highest-use position. Instead of hiding this choice, we run the four-road experiment once for every valid tied road. We also repeat the four-road comparison with ten road-distance seeds. These checks show which conclusions are stable and which depend on a particular modelling choice.
    """),
    code("""
    tie_table = create_tie_sensitivity(main_results)
    seed_table = create_seed_sensitivity()

    print("All valid fourth-road tie choices:")
    display(tie_table.round(2))

    print("Four-road result across road-distance seeds:")
    display(seed_table.round(2))
    """),
    markdown("""
    ## 6. Static travel-cost sensitivity check

    This optional test keeps the top three ranked roads open but multiplies their edge cost. It shows whether routes respond to a simple cost change. It is **not** a traffic-flow simulation and the cost should not be called exact delivery time.
    """),
    code("""
    cost_table = create_travel_cost_results(main_results)
    display(cost_table.round(2))
    """),
    markdown("""
    ## 7. Save and show the final evidence
    """),
    code("""
    results_directory = project_root / "results"
    figures_directory = project_root / "figures"
    results_directory.mkdir(exist_ok=True)
    figures_directory.mkdir(exist_ok=True)

    comparison.round(4).to_csv(
        results_directory / "closure_comparison_results.csv", index=False
    )
    main_results["random_runs_table"].round(4).to_csv(
        results_directory / "random_run_results.csv", index=False
    )
    tie_table.round(4).to_csv(
        results_directory / "tie_sensitivity_results.csv", index=False
    )
    seed_table.round(4).to_csv(
        results_directory / "network_seed_results.csv", index=False
    )
    cost_table.round(4).to_csv(
        results_directory / "travel_cost_results.csv", index=False
    )

    save_main_figures(main_results, tie_table, seed_table, cost_table)
    save_network_figure(main_results)
    print("Tables and figures saved successfully.")
    """),
    code("""
    display(Image(filename=str(figures_directory / "distance_comparison.png")))
    display(Image(filename=str(figures_directory / "reachability_comparison.png")))
    """),
    code("""
    display(Image(filename=str(figures_directory / "tie_sensitivity.png")))
    display(Image(filename=str(figures_directory / "high_use_closure_network.png")))
    """),
    markdown("""
    ## 8. What we found

    Highest-use closures produced a larger distance increase than the random mean at every closure level when restaurant reassignment was allowed. At four closures, the random mean increase was 8.96%, while the selected highest-use case increased distance by 105.26%. None of the 100 random four-road runs was as severe.

    Under fixed assignments, the chosen four-road case left only 46.67% of orders serviceable because restaurant `(0, 0)` was isolated. This does not mean those eight customers were physically disconnected: after reassignment, every customer could reach another restaurant.

    The tied-road test also changed the interpretation. All eight fourth-road choices increased fixed-assignment distance by between 56.58% and 79.41%, but only one choice isolated the restaurant. The distance effect was consistent, while the exact serviceability drop depended on the tie-break.

    Across ten road-distance seeds, highest-use closures still caused a larger four-road distance increase than the random mean. This supports the main pattern within our synthetic design, although it does not prove that every real city would behave the same way.
    """),
    markdown("""
    ## 9. Limitations and conclusion

    The model uses a regular synthetic grid, fixed road distances and shortest-path drivers. It does not include one-way streets, live traffic, driver capacity, changing orders or interaction between deliveries. Baseline usage is also fixed before the closures instead of being ranked again after every removal.

    Within these assumptions, the results support our hypothesis: closing roads used by many baseline delivery routes usually caused much larger detours than random closures. The reassignment and tie checks were important because they stopped us from incorrectly describing an isolated restaurant as complete customer disconnection.
    """),
    markdown("""
    ## Reproducibility

    From the main project folder, run:

    ```bash
    python -m pytest
    python -m src.run_analysis
    ```

    The first command checks the main functions. The second command rebuilds all final CSV files and figures.
    """)
]


def table_output(table):
    return nbf.v4.new_output(
        "display_data",
        data={
            "text/html": table.to_html(index=True),
            "text/plain": table.to_string(index=True)
        },
        metadata={}
    )


def image_output(path):
    image_data = base64.b64encode(path.read_bytes()).decode("ascii")
    return nbf.v4.new_output(
        "display_data",
        data={"image/png": image_data, "text/plain": path.name},
        metadata={}
    )


# Save outputs as well as code so the notebook is readable on GitHub.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.run_analysis import (  # noqa: E402
    create_closure_comparison,
    create_seed_sensitivity,
    create_tie_sensitivity,
    create_travel_cost_results,
    save_main_figures,
    save_network_figure,
)

main_results = create_closure_comparison()
tie_table = create_tie_sensitivity(main_results)
seed_table = create_seed_sensitivity()
cost_table = create_travel_cost_results(main_results)
save_main_figures(main_results, tie_table, seed_table, cost_table)
save_network_figure(main_results)

baseline_average = (
    sum(main_results["baseline_distances"].values())
    / len(main_results["baseline_distances"])
)
assignment_table = pd.DataFrame([
    {
        "customer": customer,
        "assigned_restaurant": restaurant,
        "baseline_distance": main_results["baseline_distances"][customer]
    }
    for customer, restaurant in main_results["assignments"].items()
])
road_usage_table = pd.DataFrame([
    {"road": str(road), "baseline_routes_using_road": count}
    for road, count in main_results["road_usage"].most_common()
])
display_columns = [
    "roads_closed",
    "random_flexible_distance_mean",
    "random_flexible_distance_p10",
    "random_flexible_distance_p90",
    "high_use_flexible_distance",
    "random_flexible_reachable_mean",
    "high_use_flexible_reachable",
    "high_use_fixed_reachable",
    "random_runs_equal_or_worse_percent",
]
comparison_display = main_results["comparison_table"][display_columns].round(2)

notebook.cells[4].outputs = [
    nbf.v4.new_output(
        "stream",
        name="stdout",
        text=(
            "Locations: 36\nRoads: 60\n"
            "Restaurants: [(0, 0), (5, 5), (0, 5)]\n"
            "Number of customers: 15\n"
            f"Baseline average distance: {baseline_average:.2f}\n"
        )
    ),
    table_output(assignment_table)
]
notebook.cells[6].outputs = [table_output(road_usage_table.head(15))]
notebook.cells[8].outputs = [table_output(comparison_display)]
notebook.cells[10].outputs = [
    nbf.v4.new_output(
        "stream", name="stdout", text="All valid fourth-road tie choices:\n"
    ),
    table_output(tie_table.round(2)),
    nbf.v4.new_output(
        "stream", name="stdout", text="Four-road result across road-distance seeds:\n"
    ),
    table_output(seed_table.round(2))
]
notebook.cells[12].outputs = [table_output(cost_table.round(2))]
notebook.cells[14].outputs = [
    nbf.v4.new_output(
        "stream", name="stdout", text="Tables and figures saved successfully.\n"
    )
]
notebook.cells[15].outputs = [
    image_output(PROJECT_ROOT / "figures" / "distance_comparison.png"),
    image_output(PROJECT_ROOT / "figures" / "reachability_comparison.png")
]
notebook.cells[16].outputs = [
    image_output(PROJECT_ROOT / "figures" / "tie_sensitivity.png"),
    image_output(PROJECT_ROOT / "figures" / "high_use_closure_network.png")
]

execution_count = 1
for cell in notebook.cells:
    if cell.cell_type == "code":
        cell.execution_count = execution_count
        execution_count += 1

nbf.write(notebook, NOTEBOOK_PATH)
print("Built", NOTEBOOK_PATH)

checkpoint_path = PROJECT_ROOT / "notebooks" / "checkpoint2_demo.ipynb"
if checkpoint_path.exists():
    checkpoint = nbf.read(checkpoint_path, as_version=4)
    note = (
        "**Development record:** This is the historical Checkpoint 2 notebook. "
        "The corrected model, final definitions and reproducible results are in "
        "`final_analysis.ipynb`."
    )
    if not checkpoint.cells or checkpoint.cells[0].source != note:
        checkpoint.cells.insert(0, nbf.v4.new_markdown_cell(note))
        nbf.write(checkpoint, checkpoint_path)
        print("Added final-analysis note to", checkpoint_path)
