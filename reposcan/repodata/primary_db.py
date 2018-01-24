import sqlite3


class PrimaryDatabaseMD:
    def __init__(self, filename):
        self.packages = []
        conn = sqlite3.connect(filename)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        for row in c.execute("select name, epoch, version, release, arch, checksum_type, pkgid from packages"):
            self.packages.append({
                "name": row["name"],
                "epoch": row["epoch"],
                "ver": row["version"],
                "rel": row["release"],
                "arch": row["arch"],
                "checksum_type": row["checksum_type"],
                "checksum": row["pkgid"]
            })
        conn.close()

    def get_package_count(self):
        return len(self.packages)

    def list_packages(self):
        return self.packages
