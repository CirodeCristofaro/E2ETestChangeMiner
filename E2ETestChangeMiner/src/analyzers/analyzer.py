from pydriller import Repository, Git
from  E2ETestChangeMiner.src.analyzers.languages.java_code_analyzer import JavaCodeAnalyzer
from  E2ETestChangeMiner.src.database.database import Database
from  E2ETestChangeMiner.src.utils.save_changes_to_sqlite import save_changes_to_sqlite


def analyze_repository(repo_url: str, file_test: str, directory: str, connectionDB: Database, repository_name) -> list[
    dict[str, str | None]]:
    """
    Analyses repositories.
    Note: The `include_deleted_files` parameter allows analyzing commits that modify a deleted file.
    This is useful when reconstructing the history of a deleted `filepath`.
    """
    repo = Repository(repo_url, include_deleted_files=True, filepath=file_test, clone_repo_to=directory)
    save_repository_sql(connectionDB, repo, repo_url, repository_name)

    parser = None
    test_files_affected = []
    for commit in repo.traverse_commits():
        for mod in commit.modified_files:
            if mod.new_path == file_test or mod.old_path == file_test:
                analyzer = JavaCodeAnalyzer()
                method_deltas, parser = analyzer.analyze_methods(mod)
                test_files_affected.append({
                    'repository_name': repository_name,
                    'commit_id': commit.hash,
                    'commit_date': commit.author_date,
                    'file': mod.new_path if mod.new_path else mod.old_path,
                    'change_type': mod.change_type.name,
                    'message_info': {
                        'commit_title': commit.msg.split('\n')[0],
                        'full_message': commit.msg,
                        'delta': mod.diff
                    },
                    'method_deltas': method_deltas
                })

    save_changes_to_sqlite(test_files_affected,  r'By\.\w+\((?:[^()"]+|"(?:\\.|[^"\\])*"|\w+\([^()]*\))+(?:\s*\+\s*(?:[^()"]+|"(?:\\.|[^"\\])*"|\w+\([^()]*\)))*\)', parser, connectionDB)

    return test_files_affected


def save_repository_sql(connectionDB:Database, repo:Repository, repo_url:str, repository_name:str) -> None:
    if "github" in repo_url:
        local_repo_path = next(repo.traverse_commits()).project_path
        repo_path = local_repo_path
    else:
        repo_path = repo_url
    gr = Git(repo_path).total_commits()
    connectionDB.insert_change_repo({
        'repository_name': repository_name,
        'total_commit': gr,
    })
