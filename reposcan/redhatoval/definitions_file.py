"""
Parse informations from OVAL definitions file.
"""

class OvalDefinitions:
    """Class parsing OVAL definitions file."""
    def __init__(self, oval_id, lastmodified, url, local_path):
        self.oval_id = oval_id
        self.lastmodified = lastmodified
        self.url = url
        self.local_path = local_path

    def load_metadata(self):
        """Parse available metadata files into memory."""

    def unload_metadata(self):
        """Unset previously loaded metadata files from this object."""
