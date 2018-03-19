"""
Module to handle /repos API calls.
"""

from utils import ListDict

class RepoDict(dict):
    """Dictionary to hold repository data, the extra id attribute
       is not supposed to be passed to json output."""
    def __init__(self, oid, *args):
        dict.__init__(self, *args)
        self.oid = oid

class RepoCache(object):
    """Cache which hold repository data and id->label, label->id mappings."""
    def __init__(self, cursor):
        self.cursor = cursor
        self.cache_id = {}
        self.cache_label = ListDict()
        self.prepare()

    def prepare(self):
        """Read repository data into memory."""
        self.cursor.execute("""SELECT r.id,
                                      cs.label,
                                      cs.name as repo_name,
                                      r.url,
                                      a.name as basearch_name,
                                      r.releasever,
                                      p.name as product_name
                                 FROM repo r
                                 JOIN content_set cs ON cs.id = r.content_set_id
                                 JOIN arch a ON a.id = r.basearch_id
                                 JOIN product p ON p.id = cs.product_id
                                 """)

        for oid, label, name, url, basearch, releasever, product in self.cursor.fetchall():
            repo_obj = RepoDict(oid, {
                "label": label,
                "name": name,
                "url": url,
                "basearch": basearch,
                "releasever": releasever,
                "product": product,
                })
            self.cache_id[oid] = repo_obj
            self.cache_label[label] = repo_obj

    def id2label(self, oid):
        """Repository id->label mapping."""
        return self.cache_id.get(oid, {}).get("label", None)

    def label2ids(self, label):
        """Repository label->[id,...] mapping."""
        return [repo.oid for repo in self.cache_label.get(label, [])]

    def get_by_label(self, label):
        """Complete repository data for given label."""
        return self.cache_label.get(label, None)


class RepoAPI(object):
    """ Main /repos API class."""
    # pylint: disable=too-few-public-methods
    def __init__(self, cursor):
        self.cache = RepoCache(cursor)

    def process_list(self, data):
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data['repository_list']
        repolist = {}
        for label in repos:
            repolist[label] = self.cache.get_by_label(label)

        response = {
            'repository_list': repolist,
        }

        return response
