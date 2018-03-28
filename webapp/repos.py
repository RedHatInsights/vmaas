"""
Module to handle /repos API calls.
"""

from utils import ListDict, format_datetime


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
        self.cache_repo_product_id = {}
        self.cache_product_repo_id = ListDict()
        self.prepare()

    def prepare(self):
        """Read repository data into memory."""
        self.cursor.execute("""SELECT r.id,
                                      cs.label,
                                      cs.name as repo_name,
                                      r.url,
                                      a.name as basearch_name,
                                      r.releasever,
                                      p.name as product_name,
                                      p.id as product_id,
                                      r.revision
                                 FROM repo r
                                 JOIN content_set cs ON cs.id = r.content_set_id
                                 JOIN arch a ON a.id = r.basearch_id
                                 JOIN product p ON p.id = cs.product_id
                                 """)

        for oid, label, name, url, basearch, releasever, product, product_id, revision in self.cursor.fetchall():
            repo_obj = RepoDict(oid, {
                "label": label,
                "name": name,
                "url": url,
                "basearch": basearch,
                "releasever": releasever,
                "product": product,
                "revision": format_datetime(revision),
                })
            self.cache_id[oid] = repo_obj
            self.cache_label[label] = repo_obj
            # repo_id -> product_id
            self.cache_repo_product_id[oid] = product_id
            # product_id -> [repo_id]
            self.cache_product_repo_id[product_id] = oid

    def id2label(self, oid):
        """Repository id->label mapping."""
        return self.cache_id.get(oid, {}).get("label", None)

    def label2ids(self, label):
        """Repository label->[id,...] mapping."""
        return [repo.oid for repo in self.cache_label.get(label, [])]

    def get_by_id(self, oid):
        """Complete repository data for given id."""
        return self.cache_id.get(oid, None)

    def get_by_label(self, label):
        """Complete repository data for given label."""
        return self.cache_label.get(label, None)

    def all_ids(self):
        """IDs of all known repositories."""
        return self.cache_id.keys()

    def id2productid(self, oid):
        """Repository id -> Product id mapping."""
        return self.cache_repo_product_id.get(oid, None)

    def productid2ids(self, product_id):
        """Product id -> [repo_id,...] mapping."""
        return self.cache_product_repo_id.get(product_id, [])


class RepoAPI(object):
    """ Main /repos API class."""
    # pylint: disable=too-few-public-methods
    def __init__(self, repocache):
        self.cache = repocache

    # pylint: disable=no-self-use
    def is_empty(self, data):
        """
        Checks for null/empty/blank list on input
        """
        return not (data and data['repository_list'] and data['repository_list'][0])

    def process_list(self, data):
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data['repository_list'] if not self.is_empty(data) else self.cache.cache_label

        response = {'repository_list': None}

        if self.is_empty(data):
            response['repository_list'] = self.cache.cache_label.keys()
        else:
            repolist = {}
            repos = data['repository_list']
            for label in repos:
                repolist[label] = self.cache.get_by_label(label)
            response['repository_list'] = repolist

        return response
