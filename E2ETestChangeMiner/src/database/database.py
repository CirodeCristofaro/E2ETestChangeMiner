import sqlite3
from typing import List, Tuple
from  E2ETestChangeMiner.src.config.configuration import QUERY_GET_ALL_TESTING, INSERT_INTO_CHANGES, \
    INSERT_INTO_REPO, QUERY_FIND_REPOSITORY_BY_NAME, QUERY_UPDATE_REPOSITORY_TOTAL_COMMIT


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Opens the database connection"""
        try:
            if self.connection is None:  # Avoids reconnecting if already connected
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

    def get_rows(self) -> List[Tuple]:
        """Retrieves rows from the database and applies a filter to test file paths"""
        try:
            rows = self.get_all_testing()
            print(f"Rows extracted: {len(rows)}")
            return rows
        except Exception as e:
            print(f"An error occurred during the operation: {e}")
            raise

    @staticmethod
    def extract_name_file(rows: List[Tuple]) -> List[Tuple]:
        """Modifies file paths by replacing '/' with '\\' and removes the initial part of the name in the test path"""
        modified_rows = []
        for i, row in enumerate(rows):
            name = row[0].replace('/', '_')
            file_path = row[1]
            prefix = f"/{name}/"
            if file_path.startswith(prefix):
                file = file_path.replace(prefix, '').replace('/', '\\')
            else:
                file = file_path
            modified_row = (row[0], file, *row[2:])
            modified_rows.append(modified_row)
        return modified_rows

    def get_all_testing(self) -> List[Tuple]:
        """Executes a query to retrieve all rows from the table and modifies their paths"""
        try:
            cursor = self.connection.cursor()  # Open the cursor
            cursor.execute(QUERY_GET_ALL_TESTING)
            rows = cursor.fetchall()
            return self.extract_name_file(rows)
        except sqlite3.Error as e:
            raise RuntimeError(f"Error during query execution: {e}")


    def create_table(self, name_table: str) -> None:
        """Creates a table in the SQLite database"""
        try:
            c = self.connection.cursor()
            c.execute(name_table)
        except sqlite3.Error as e:
            raise RuntimeError(f"Error during query execution: {e}")

    def insert_change_repo(self, change):
        """Inserts a new row into the 'changes' table only if it does not already exist,
        and updates total_commit if the existing one is lower."""
        cur = self.connection.cursor()

        # Checks if the repository already exists
        cur.execute(QUERY_FIND_REPOSITORY_BY_NAME, (change["repository_name"],))
        existing_record = cur.fetchone()

        if existing_record:
            # If the existing total_commit is lower than the passed one, update it
            if existing_record[1] < change["total_commit"]:  # Assuming total_commit is in the second position
                cur.execute(QUERY_UPDATE_REPOSITORY_TOTAL_COMMIT,
                            (change["total_commit"], change["repository_name"]))
                self.connection.commit()
            return existing_record[1]

        # If it does not exist, insert the new record
        cur.execute(INSERT_INTO_REPO, (change["repository_name"], change["total_commit"]))
        self.connection.commit()

        return cur.lastrowid

    def insert_change(self, change):
        """Inserts a new row into the 'changes' table"""
        cur = self.connection.cursor()
        cur.execute(INSERT_INTO_CHANGES, (
            change["repository_name"], change["Commit ID"], change["Commit Date"],
            change["Commit Title"], change["Full Message"], change["Delta"],
            change["Modified File"], change["File Change Type"], change["Change Type"],
            change["Method Name"], change["Old Name"], change["New Name"],
            change["Statement/Assertions Removed"], change["Statement/Assertions Added"],
            change["Statement/Assertions Modified"], change["Before Selector"],
            change["After Selector"]
        ))
        self.connection.commit()
        return cur.lastrowid
