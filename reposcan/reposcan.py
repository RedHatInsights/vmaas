#!/usr/bin/python3

import sys

from repodata.repository_controller import RepositoryController

if __name__ == '__main__':
    repository_controller = RepositoryController()
    for repo_url in sys.argv[1:]:
        repository_controller.add_repository(repo_url)
    repository_controller.store()
