import os
import time
from  E2ETestChangeMiner.src.analyzers.analyzer import analyze_repository
from  E2ETestChangeMiner.src.config.configuration import GIT_REPO_DIR, DB_REPORT_PATH, DATABASE_PATH, CREATE_TABLE_REPO, CREATE_TABLE_CHANGES
from  E2ETestChangeMiner.src.database.database import Database


def main():
    # Connect to the e2egit database
    db = Database(DATABASE_PATH)
    db.connect()
    rows = db.get_rows()
    db.disconnect()

    # Connect to the report database
    db_report = Database(DB_REPORT_PATH)
    db_report.connect()  # Connect to the report database
    db_report.create_table(CREATE_TABLE_CHANGES)  # Create the table in the report database
    db_report.create_table(CREATE_TABLE_REPO)

    for row in rows:
        repository_url = 'https://github.com/' + row[0]
        print(repository_url)
        repo_dir, exists = __dir_git_repo(row[0])
        if exists:
            repository_url = repo_dir
        repository_name = row[0]

        while True:
            try:
                print(f"Repository name: {row[0]}, Testing file: {row[1]}")
                analyze_repository(repository_url, row[1], repo_dir, db_report, repository_name)
                break
            except Exception as e:
                print(f"Error analyzing {row[0]}: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)

    db_report.disconnect()


def __dir_git_repo(repo_dir: str):
    repo_dir = repo_dir.replace("/", "\\")
    main_dir = repo_dir.split("\\")[0]
    target_dir = os.path.join(GIT_REPO_DIR, main_dir)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        return target_dir.replace("\\", "/"), False
    else:
        target_dir = os.path.join(GIT_REPO_DIR, repo_dir)

    return target_dir.replace("\\", "/"), True


if __name__ == "__main__":
    print("Analysis in progress...")
    main()
