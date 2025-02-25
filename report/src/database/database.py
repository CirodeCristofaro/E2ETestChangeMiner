import sqlite3

from report.src.config.configuration import CREATE_TABLE_REPOSITORY_CHANGES_SUMMORY, INSERT_INTO_REPOSITORY_CHANGES_SUMMORY, \
    QUERY_TOT_INIT, UPDATE_REPOSITORY_CHANGES_SUMMORY, \
    GET_ALL_REPOSITORY_CHANGES_SUMMORY_CONDITION, INSERT_INTO_SELECTOR_SUMMORY, QUERY_SUM_REPOSITORY_CHANGES_SUMMERY


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Opens the connection to the database"""
        try:
            if self.connection is None:  # Prevent reconnecting if already connected
                self.connection = sqlite3.connect(self.db_path)
                print(f"Database connection successful: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            raise RuntimeError(f"Error during database connection: {e}")

    def disconnect(self) -> None:
        """Closes the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Database connection closed.")

    def get_rows(self,get_query:str):
        """Fetches rows from the REPOSITORY_CHANGES_SUMMORY table in the database"""
        try:
            cursor = self.connection.cursor()  # Open the cursor
            cursor.execute(get_query)
            rows = cursor.fetchall()
            print(f"Rows extracted: {len(rows)}")
            return rows
        except Exception as e:
            print(f"An error occurred during the operation: {e}")
            raise


    def get_rows_changes_repo_name(self, get_query: str,repo_name):
        """Fetches rows from the REPOSITORY_CHANGES_SUMMORY table in the database"""
        try:
            cursor = self.connection.cursor()  # Open the cursor
            cursor.execute(get_query,repo_name)
            rows = cursor.fetchall()
            print(f"Rows extracted: {len(rows)}")
            return rows
        except Exception as e:
            print(f"An error occurred during the operation: {e}")
            raise


    def create_table_report(self):
        """Creates a table in the SQLite database"""
        try:
            c = self.connection.cursor()
            c.execute(CREATE_TABLE_REPOSITORY_CHANGES_SUMMORY)
            print("Table created successfully.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Error during query execution: {e}")

    def create_table(self,table_name:str):
        """Creates a table in the SQLite database"""
        try:
            c = self.connection.cursor()
            c.execute(table_name)
            print("Table created successfully.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Error during query execution: {e}")

    def insert_analyzer_entry(self, change):
        """Inserts a new row into the REPOSITORY_CHANGES_SUMMORY table"""
        cur = self.connection.cursor()
        cur.execute(INSERT_INTO_REPOSITORY_CHANGES_SUMMORY, (
            change["repository_name"], change["total_commit"], change["commit_tot"], change["commit_added"],
            change["commit_rename"], change["commit_deleted"], change["commit_modified"],
            change["commit_modify_selector"],
            change["changed_from_By_id"], change["remained_By_id"],
            change["total_changed_from_By_name"], change["remained_By_name"],
            change["changed_from_By_className"], change["remained_By_className"],
            change["changed_from_By_tagName"], change["remained_By_tagName"],
            change["changed_from_By_linkText"], change["remained_By_linkText"],
            change["changed_from_By_partialLinkText"], change["remained_By_partialLinkText"],
            change["changed_from_By_cssSelector"], change["remained_By_cssSelector"],
            change["changed_from_By_xpath"], change["remained_By_xpath"]
        ))
        self.connection.commit()
        return cur.lastrowid

    def insert_totals_from_query(self):
        """Executes the aggregation query and inserts or updates the results into the 'repository_changes_summary' table only if the data has changed."""

        try:
            cur = self.connection.cursor()
            cur.execute(QUERY_TOT_INIT)
            # Fetch the query results
            results = cur.fetchall()
            combined_results = []

            for row in results:

                cur.execute(QUERY_SUM_REPOSITORY_CHANGES_SUMMERY, (row[0],))
                # Retrieve the current values for the repository_name
                res=cur.fetchall()
                for r in res:
                    # Add the columns from the first query (9 columns) with the columns from the second query
                    combined_row = row + r  # Merge the rows (tuple with 9 columns + other columns from res)
                    combined_results.append(combined_row)
                for rows in combined_results:
                    cur.execute(GET_ALL_REPOSITORY_CHANGES_SUMMORY_CONDITION, (rows[0],))
                    existing_row = cur.fetchone()
                    # If the row exists and the values are different, perform the update
                    if existing_row:
                        # Compare all the fields except repository_name
                        # Strip the values to avoid extra spaces and ensure they are the same type
                        if existing_row[1:] != row[1:]:
                            # Values have changed, update the row
                            cur.execute(UPDATE_REPOSITORY_CHANGES_SUMMORY, rows)
                            #print(f"Data updated for repository: {rows[0]}")
                    else:
                        # Row doesn't exist, insert it
                        cur.execute(INSERT_INTO_REPOSITORY_CHANGES_SUMMORY, rows)
                        #print(f"Data inserted for repository: {rows[0]}")

            # Commit the changes
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error during data insertion or update: {e}")
            self.connection.rollback()

    def insert_totals_from_query_selector(self, selector_summary):
        cur = self.connection.cursor()
        values = (
            selector_summary.repository_name,
            selector_summary.commit_id,
            selector_summary.delta,
            selector_summary.modified_file,
            selector_summary.type_of_change_to_the_file,
            selector_summary.type_of_change_to_the_method,
            selector_summary.method_name,
            selector_summary.statement_removed,
            selector_summary.statement_added,
            selector_summary.statement_modified,
            selector_summary.before_selector,
            selector_summary.after_selector,
            selector_summary.changed_from_by_id,
            selector_summary.remained_by_id,
            selector_summary.changed_from_by_name,
            selector_summary.remained_by_name,
            selector_summary.changed_from_by_className,
            selector_summary.remained_by_className,
            selector_summary.changed_from_by_tagName,
            selector_summary.remained_by_tagName,
            selector_summary.changed_from_by_linkText,
            selector_summary.remained_by_linkText,
            selector_summary.changed_from_by_partialLinkText,
            selector_summary.remained_by_partialLinkText,
            selector_summary.changed_from_by_cssSelector,
            selector_summary.remained_by_cssSelector,
            selector_summary.changed_from_by_xpath,
            selector_summary.remained_by_xpath
        )

        cur.execute(INSERT_INTO_SELECTOR_SUMMORY, values)
        self.connection.commit()
        return cur.lastrowid

