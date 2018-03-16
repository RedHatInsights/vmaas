"""
Module to handle /repos API calls.
"""

class RepoAPI(object):
    """ Main /repos API class."""
    # pylint: disable=too-few-public-methods
    def __init__(self, cursor):
        self.cursor = cursor

    def process_list(self, data):
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data['repository_list']
        response = {}
        if not repos:
            return response

        repolist = {}
        # Select all packages with given evrs ids and put them into dictionary
        self.cursor.execute("select label, url from repo where label in %s;", [tuple(repos)])
        for label, url in self.cursor.fetchall():
            repolist[label] = {
                "url": url,
            }

        response['repository_list'] = repolist

        return response
