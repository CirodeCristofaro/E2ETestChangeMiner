import os
import time


from report.src.config.configuration import  DIR_CHARTS, GET_ALL_REPOSITORY_CHANGES_SUMMORY, \
  SUM_REPOSITPORY_SUMMARY

from report.src.database.db_manager import selectors_summary, generate_repository_changes_summary, connect_db
from report.src.model.repository_change_summary import RepositoryChangeSummary
from report.src.model.total_summary import TotalSummary
from report.src.util.chart_generator import graph_repository_changes_summary, graph_total_summary



def main():
    # Start timing the execution
    start_time = time.time()

    db = connect_db()
    # Fetch total summary data and generate its chart
    rows = db.get_rows(SUM_REPOSITPORY_SUMMARY)

    total_summary = TotalSummary(rows[0])
    graph_total_summary(total_summary)
    print(f"Execution time: {time.time() - start_time:.2f} seconds -> total summary")
    print(f"Charts saved in the folder: {DIR_CHARTS}")

    # Disconnect from the database
    db.disconnect()


def graph_generate_repository_summary():
    start_time = time.time()
    db=connect_db()
    # Fetch all repository changes summary data
    rows = db.get_rows(GET_ALL_REPOSITORY_CHANGES_SUMMORY)
    # Create a list of RepositoryChangeSummary objects from the fetched rows
    repositories = [RepositoryChangeSummary(row) for row in rows]
    # Ensure the directory for charts exists
    os.makedirs(DIR_CHARTS, exist_ok=True)
    # Generate charts for each repository's changes summary
    graph_repository_changes_summary(repositories)
    print(f"Execution time: {time.time() - start_time:.2f} seconds ->repository changes summary")


if __name__ == '__main__':
    selectors_summary()
    generate_repository_changes_summary()
    main()



