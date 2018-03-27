"""
Module containing class for Primary SQLite metadata.
"""
import sqlite3


class PrimaryDatabaseMD:
    """Class parsing Primary SQLite. Takes filename in the constructor."""
    def __init__(self, filename):
        self.packages = []
        conn = sqlite3.connect(filename)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        for row in cur.execute("select name, epoch, version, release, arch, summary, description, checksum_type, pkgid from packages"):
            self.packages.append({
                "name": row["name"],
                "epoch": row["epoch"],
                "ver": row["version"],
                "rel": row["release"],
                "arch": row["arch"],
                "summary": row["summary"],
                "description": row["description"],
                "checksum_type": row["checksum_type"],
                "checksum": row["pkgid"]
            })
        conn.close()

    def get_package_count(self):
        """Returns count of packages in Primary SQLite file."""
        return len(self.packages)

    def list_packages(self):
        """Returns list of parsed packages (list of dictionaries)."""
        return self.packages
