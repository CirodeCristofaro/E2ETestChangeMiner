import re

from report.src.config.configuration import DATABASE_PATH, GET_ALL_REPOSITORY, CREATE_TABLE_SELECTOR_SUMMARY, \
    GET_CHANGES_FROM_NAME
from report.src.database.database import Database
from report.src.model.selector_summary import SelectorSummary


def selectors_summary():
    db, rows_repo = generate_selector_summary()
    # Populate the selector summary table for each repository
    for repo in rows_repo:
        rows = db.get_rows_changes_repo_name(GET_CHANGES_FROM_NAME, repo)
        populate_table_selectors(rows, db)
    # Disconnect from the database
    db.disconnect()

def generate_repository_changes_summary():
    db = connect_db()
    # Create a table for the report and insert total data
    db.create_table_report()
    db.insert_totals_from_query()
    return db


def connect_db():
    db = Database(DATABASE_PATH)
    db.connect()
    return db


def generate_selector_summary():
    # Initialize and connect to the database
    db = Database(DATABASE_PATH)
    db.connect()
    # Fetch all repository data and create a table for selector summary
    rows_repo = db.get_rows(GET_ALL_REPOSITORY)
    db.create_table(CREATE_TABLE_SELECTOR_SUMMARY)
    return db, rows_repo

def populate_table_selectors(rows, db):
    # Create a list of SelectorSummary objects from the fetched rows
    selector_summary = [SelectorSummary(row) for row in rows]

    # Process each selector and update the summary table
    for selector in selector_summary:
        if selector.before_selector and selector.after_selector:
            before_list, after_list = extract_selector(selector.before_selector, selector.after_selector,r"By[^()]*(?=\()")
            max_length = max(len(before_list), len(after_list))

            for i in range(max_length):
                before = before_list[i]
                after = after_list[i]

                if before == after:
                    increment_field(selector, f"remained_{before.lower().split('.')[0]}_{before.split('.')[1]}")
                else:
                    increment_field(selector, f"changed_from_{before.lower().split('.')[0]}_{before.split('.')[1]}")
            db.insert_totals_from_query_selector(selector)



def increment_field(selector, field_name):
    # Increment the specified field in the selector object
    if hasattr(selector, field_name):
        setattr(selector, field_name, getattr(selector, field_name) + 1)


def extract_selector(select1: str, select2: str, pattern: str):
    # Extract the selector type using a regex pattern
    matches = []
    for match in re.finditer(pattern, select1):
        matches.append(match.group(0))

    matches2 = []
    for match in re.finditer(pattern, select2):
        matches2.append(match.group(0))

    return matches,matches2
