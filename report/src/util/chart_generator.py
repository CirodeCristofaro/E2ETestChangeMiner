import os
from typing import List

from matplotlib import pyplot as plt
import seaborn as sns
from report.src.model.repository_change_summary import RepositoryChangeSummary
from report.src.model.total_summary import TotalSummary
from report.src.util.file_manager import create_dir


def graph_total_summary(total_summary: TotalSummary) -> None:
    # Create a directory for the total summary charts
    repo_name = "Total_Summary"
    repo_folder = create_dir(repo_name)

    # # Define labels and values for the bar chart
    # labels_bar = ["Commits modifying tests"]
    # percentage = total_summary.percentage_commits_test()
    # total_commits_test = total_summary.total_commits_test
    # values_bar = [percentage]
    # annotations = [f"{percentage:.2f}%  (commit tests: {total_commits_test})"]
    # total_commits = total_summary.total_commits()
    # colors = ["#1f77b4"]
    #
    # # Generate the bar chart for commits modifying tests
    # generate_bar_chart(
    #     labels_bar, values_bar, colors, repo_name, "Percentage of Commits Modifying Tests",
    #     "Type of modification", "Percentage of Changes", repo_folder, repo_name, "distribution", total_commits,
    #     f"Total repository: {total_summary.total_repository}, Total Commits:",
    #     annotations
    # )
    labels_bar = ["by.id", "by.className", "by.Name","by.tagName","by.linkText","by.partialLinkText","by.cssSelector","by.xpath"]
    values_bar = [
        total_summary.percentage_by_id_changes_selectors(),
        total_summary.percentage_by_className_changes_selectors(),
        total_summary.percentage_by_name_changes_selectors(),
        total_summary.percentage_by_tagName_changes_selectors(),
        total_summary.percentage_by_linkText_changes_selectors(),
        total_summary.percentage_by_partialLinkText_changes_selectors(),
        total_summary.percentage_by_cssSelector_changes_selectors(),
        total_summary.percentage_by_xpath_changes_selectors()
    ]

    total_commits = total_summary.total_selector_modify
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]

    # Generate the bar chart for distribution of test commit changes
    generate_bar_chart(
        labels_bar, values_bar, colors, repo_name, "Distribution of changed selectors",
        "Selector type", "Percentage of Changes", repo_folder, repo_name, "distribution_selector_changed", total_commits,
        f"Total repository: {total_summary.total_repository}, Total commit tests: {total_summary.total_commits_test}, Total Selector modify:"
    )

    labels_bar = ["by.id", "by.className", "by.Name", "by.tagName", "by.linkText", "by.partialLinkText",
                  "by.cssSelector", "by.xpath"]
    values_bar = [total_summary.percentage_by_id_unchanged_selectors(),
                  total_summary.percentage_by_className_unchanged_selectors(),
                  total_summary.percentage_by_name_unchanged_selectors(),
                  total_summary.percentage_by_tagName_unchanged_selectors(),
                  total_summary.percentage_by_linkText_unchanged_selectors(),
                  total_summary.percentage_by_partialLinkText_unchanged_selectors(),
                  total_summary.percentage_by_cssSelector_unchanged_selectors(),
                  total_summary.percentage_by_xpath_unchanged_selectors()]
    total_commits = total_summary.total_selector_modify
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]

    # Generate the bar chart for distribution of test commit changes
    generate_bar_chart(
        labels_bar, values_bar, colors, repo_name, "Distribution of unchanged selectors",
        "Selector type", "Percentage of Changes", repo_folder, repo_name, "distribution_selector_unchanged", total_commits,
        f"Total repository: {total_summary.total_repository}, Total commit tests: {total_summary.total_commits_test}, Total Selector modify:"
    )


    #generate_selector_change_charts(total_summary,repo_name,repo_folder)


def generate_selector_change_charts(total_summary: TotalSummary,repo_name:str,repo_folder) -> None:
    # Define data for selector changes
    selector_data = [
        ("by.id", total_summary.percentage_by_id_changes_selectors(),
         total_summary.percentage_by_id_unchanged_selectors()),
        ("by.className", total_summary.percentage_by_className_changes_selectors(),
         total_summary.percentage_by_className_unchanged_selectors()),
        ("by.Name", total_summary.percentage_by_name_changes_selectors(),
         total_summary.percentage_by_name_unchanged_selectors()),
        ("by.tagName", total_summary.percentage_by_tagName_changes_selectors(),
         total_summary.percentage_by_tagName_unchanged_selectors()),
        ("by.linkText", total_summary.percentage_by_linkText_changes_selectors(),
         total_summary.percentage_by_linkText_unchanged_selectors()),
        ("by.partialLinkText", total_summary.percentage_by_partialLinkText_changes_selectors(),
         total_summary.percentage_by_partialLinkText_unchanged_selectors()),
        ("by.cssSelector", total_summary.percentage_by_cssSelector_changes_selectors(),
         total_summary.percentage_by_cssSelector_unchanged_selectors()),
        ("by.xpath", total_summary.percentage_by_xpath_changes_selectors(),
         total_summary.percentage_by_xpath_unchanged_selectors())
    ]
    # Define colors for the charts
    colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf", "#f0e442", "#7c4dff", "#ff00ff", "#ff6347", "#32cd32", "#00ced1"
    ]
    total_commits = total_summary.total_commits_test
    # Generate bar charts for each selector type
    for selector_type, changed, unchanged in selector_data:
        labels_selectors = [f"Selectors {selector_type} changed", f"Selectors {selector_type} unchanged"]
        values_selectors = [changed, unchanged]
        generate_bar_chart(
            labels_selectors, values_selectors, colors, repo_name, f"Selector Changes - {selector_type}",
            "Selector Type", "Percentage of Changes", repo_folder, repo_name, f"selector_{selector_type}",
            total_commits,
            "Total Commit Tests:"
        )


def graph_repository_changes_summary(repositories: List[RepositoryChangeSummary]) -> None:
    # Generate charts for each repository's changes summary
    for repo in repositories:
        repo_name = repo.repository_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        repo_folder = create_dir(repo_name)

        # Define labels and values for the bar chart
        labels_bar = ["Commits modifying tests"]
        percentage = repo.percentage_commits_test()
        total_commits_test = repo.total_commits_test
        values_bar = [percentage]
        annotations = [f"{percentage:.2f}%  (commit tests: {total_commits_test})"]
        total_commits = repo.total_commits()
        colors = ["#1f77b4"]

        # Generate the bar chart for commits modifying tests
        generate_bar_chart(
            labels_bar, values_bar, colors, repo.repository_name, "Percentage of Commits Modifying Tests",
            "Type of modification", "Percentage of Changes", repo_folder, repo_name, "distribution", total_commits,
            "Total Commits:",
            annotations
        )

        # Define labels and values for the distribution of test commit changes
        labels_bar = ["Added", "Modified", "Deleted"]
        values_bar = [repo.percentage_added(), repo.percentage_modified(), repo.percentage_deleted()]
        total_commits = repo.total_commits_test
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

        # Generate the bar chart for distribution of test commit changes
        generate_bar_chart(
            labels_bar, values_bar, colors, repo.repository_name, "Distribution of test commit changes",
            "Type of modification", "Percentage of Changes", repo_folder, repo_name, "distributionTests", total_commits,
            "Total Commit Tests:"
        )

        # Define data for selector changes
        selector_data = [
            ("by.id", repo.percentage_by_id_changes_selectors(), repo.percentage_by_id_unchanged_selectors()),
            ("by.className", repo.percentage_by_className_changes_selectors(),
             repo.percentage_by_className_unchanged_selectors()),
            ("by.Name", repo.percentage_by_name_changes_selectors(), repo.percentage_by_name_unchanged_selectors()),
            ("by.tagName", repo.percentage_by_tagName_changes_selectors(),
             repo.percentage_by_tagName_unchanged_selectors()),
            ("by.linkText", repo.percentage_by_linkText_changes_selectors(),
             repo.percentage_by_linkText_unchanged_selectors()),
            ("by.partialLinkText", repo.percentage_by_partialLinkText_changes_selectors(),
             repo.percentage_by_partialLinkText_unchanged_selectors()),
            ("by.cssSelector", repo.percentage_by_cssSelector_changes_selectors(),
             repo.percentage_by_cssSelector_unchanged_selectors()),
            ("by.xpath", repo.percentage_by_xpath_changes_selectors(), repo.percentage_by_xpath_unchanged_selectors())
        ]

        # Define colors for the charts
        colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
            "#bcbd22", "#17becf", "#f0e442", "#7c4dff", "#ff00ff", "#ff6347", "#32cd32", "#00ced1"
        ]
        total_commits = repo.total_commits_test

        # Generate bar charts for each selector type
        for selector_type, changed, unchanged in selector_data:
            labels_selectors = [f"Selectors {selector_type} changed", f"Selectors {selector_type} unchanged"]
            values_selectors = [changed, unchanged]
            generate_bar_chart(
                labels_selectors, values_selectors, colors, repo.repository_name, f"Selector Changes - {selector_type}",
                "Selector Type", "Percentage of Changes", repo_folder, repo_name, f"selector_{selector_type}",
                total_commits,
                "Total Commit Tests:"
            )


def generate_bar_chart(labels, values, palette, repo_name, title, xlabel, ylabel, repo_folder, repo_name_safe,
                       chart_name, total_commits=None, total_commits_label=None, annotations=None):
    # Create a bar chart with the given data
    plt.figure(figsize=(10, 6))

    # Select only the necessary colors
    num_bars = len(labels)
    palette = palette[:num_bars]

    # Plot the bar chart
    ax = sns.barplot(x=labels, y=values, hue=labels, palette=palette, legend=False,width =0.4)
    ax.set_ylim(0, 100)

    # Add custom annotations if provided
    for i, p in enumerate(ax.patches):
        height = p.get_height()
        y_pos = height if height != 0.0 else 0.02
        annotation_text = f'{height:.2f}%'
        if annotations and i < len(annotations):
            annotation_text = annotations[i]
        ax.annotate(annotation_text, (p.get_x() + p.get_width() / 2., y_pos),
                    ha='center', va='bottom', fontsize=12, color='black', xytext=(0, 5), textcoords='offset points')

    # Set labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"{repo_name} - {title}")
    plt.xticks(rotation=0)

    # Add total commits text if provided
    if total_commits is not None and total_commits_label is not None:
        plt.text(0.95, 0.95, f"{total_commits_label} {total_commits}", ha='right', va='top',
                 fontsize=12, color='black', transform=plt.gca().transAxes)

    # Save the chart and close the plot
    plt.tight_layout()
    plt.savefig(os.path.join(repo_folder, f"{repo_name_safe}_{chart_name}.png"))
    plt.close()