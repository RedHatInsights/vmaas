#!/usr/bin/env python3
"""Export DB cache as YAML for unit tests."""

import shelve
import sys
import yaml

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
                data = yaml.full_load(stream)
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
    if len(sys.argv) != 3:
        print("Usage:\n./yaml_cache.py <vmaas.dbm path> <yaml output>")
        sys.exit(1)

    CACHE = YamlCache(filename=sys.argv[1])
    CACHE.load_shelve()
    CACHE.dump(output=sys.argv[2])
