#!/usr/bin/env python3
"""Export DB cache as YAML for unit tests."""

import shelve
import sys
import yaml
import decimal
import sqlite3
import os

sys.path.append("..")
from cache import Cache  # pylint: disable=C0413


class YamlCache(Cache):
    """YamlCache class. Dump dictionaries from Cache in YAML format."""

    def __init__(self, filename):  # pylint: disable=W0231
        """Override Cache.__init__, avoid calling Cache.reload()"""
        self.filename = filename
        self.clear()

    def load_shelve(self):
        """Use Cache.load() for loading shelve dump."""
        super().load(self.filename)

    def load_yaml(self):
        """Load cache from YAML file."""
        with open(self.filename, "r") as stream:
            try:
                # FIXME: workaround using UnsafeLoader because https://github.com/yaml/pyyaml/issues/380
                data = yaml.load(stream, Loader=yaml.UnsafeLoader)
            except yaml.YAMLError as err:
                print(err)

        for key, val in data.items():
            setattr(self, key, val)
        return self

    def dump(self, output):
        """Dump YAML with all dictionaries."""
        attrs = vars(self)
        del attrs["filename"]

        with open(output, "w") as file:
            yaml.dump(attrs, file)

    def dump_sqlite(self, output):
        if os.path.isfile(output):
            os.remove(output)

        with open('vmaas_cache_init.sql') as f_init_sql:
            with sqlite3.connect(output) as conn:
                cur = conn.cursor()
                cur.executescript(f_init_sql.read())
                self.fill_id2name_table(cur, self.id2packagename, 'id2packagename')
                self.fill_updates_table(cur, self.updates)

                self.fill_id2name_table(cur, self.id2arch, 'id2arch')
                self.fill_id2name_table(cur, self.errataid2name, 'errataid2name')

    @staticmethod
    def fill_id2name_table(cursor, dic, table):
        for id, name in dic.items():
            cursor.execute('insert into %s (id, name) values (?,?)' % table, (id, name))

    @staticmethod
    def fill_updates_table(cursor, dic):
        for pkgname_id, archs in dic.items():
            for arch_id, pkgs_ids in archs.items():
                cursor.execute('insert into updates (pkgname_id, arch_id, pkg_ids) values (?,?,?)',
                               (pkgname_id, arch_id, str(pkgs_ids)))

    def dump_shelve(self, output):
        """Dump data to Shelve file"""
        attrs = vars(self)
        del attrs["filename"]

        with shelve.open(output, 'c') as dump:
            for key, val in attrs.items():
                for name, data in val.items():
                    if isinstance(name, tuple):
                        name = ':'.join([f"{item}" for item in name])
                    dump[f"{key}:{name}"] = data


def load_test_cache():
    """Load cache with testing data."""
    cache = YamlCache("test/data/cache.yml")
    return cache.load_yaml()


if __name__ == "__main__":
    input_path = 'data/cache.yml'
    output_path = 'full_vmaas_dump.db'

    CACHE = YamlCache(filename=input_path)
    # CACHE.load_shelve()
    CACHE.load_yaml()
    CACHE.dump_sqlite(output_path)
    # CACHE.dump(output=output_path)
