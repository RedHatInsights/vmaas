"""
NEVRA elastic document.
"""
from elasticsearch_dsl import Document, Index, Text, Keyword

PACKAGES_INDEX = Index("packages")

@PACKAGES_INDEX.document
class Nevra(Document):
    """ Class representing NEVRA document in the elastic. """
    name = Keyword()
    epoch = Keyword()
    version = Keyword()
    release = Keyword()
    arch = Keyword()
    summary = Text()
    description = Text()
    source_pkg = Keyword()
    repo_label = Keyword(multi=True)

    class Index:
        """ Index name where documents belong. """
        name = "packages"
