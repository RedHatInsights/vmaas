"""
Module containing class for Primary SQLite metadata.
"""
import sqlite3

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.repodata.metadata_validators import validate_field, ValidationError
from vmaas.reposcan.mnm import VALIDATION_FAILED_ITEMS, VALIDATION_TOTAL_ITEMS


class PrimaryDatabaseMD:
    """Class parsing Primary SQLite. Takes filename in the constructor."""

    def __init__(self, filename):
        self.logger = get_logger(__name__)
        self.packages = []
        conn = sqlite3.connect(filename)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = """
            select name, epoch, version, release, arch,
                   summary, description, rpm_sourcerpm
              from packages"""
        for row in cur.execute(sql):
            VALIDATION_TOTAL_ITEMS.labels(metadata_type='primary_db').inc()
            try:
                package = self._parse_package(row)
                self.packages.append(package)
            except ValidationError as err:
                self.logger.warning("Validation failed, skipped package: %s", str(err))
        conn.close()

    def _validate(self, value, field_type):
        """Validate a field and track metrics on failure"""
        try:
            return validate_field(value, field_type)
        except ValidationError:
            VALIDATION_FAILED_ITEMS.labels(metadata_type='primary_db', field=field_type).inc()
            raise

    def _parse_package(self, row):
        """Parse and validate a single package row"""
        return {
            "name": self._validate(row["name"], 'name'),
            "epoch": row["epoch"],
            "ver": self._validate(row["version"], 'version'),
            "rel": self._validate(row["release"], 'release'),
            "arch": self._validate(row["arch"], 'arch'),
            "summary": row["summary"],
            "description": row["description"],
            "srpm": row["rpm_sourcerpm"]
        }

    def get_package_count(self):
        """Returns count of packages in Primary SQLite file."""
        return len(self.packages)

    def list_packages(self):
        """Returns list of parsed packages (list of dictionaries)."""
        return self.packages
