import os

from report.src.config.configuration import DIR_CHARTS


def create_dir(repo_name):
    # Create a directory for the repository's charts
    repo_folder = os.path.join(DIR_CHARTS, repo_name)
    os.makedirs(repo_folder, exist_ok=True)
    return repo_folder