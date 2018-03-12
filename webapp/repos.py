import sys
import ujson

class RepoAPI:
    def __init__(self, cursor):
        self.cursor = cursor

    def process_list(self, data):
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data['repository_list']
        if not repos:
            return response

        repolist = {}
        # Select all packages with given evrs ids and put them into dictionary
        self.cursor.execute("select name, url from repo where name in %s;",  [tuple(repos)])
        for name, url in self.cursor.fetchall():
            repolist[name] = {
                "url": url,
            }

        response = {
            'repository_list': repolist,
        }
        return response
