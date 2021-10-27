#!/usr/bin/env python3
"""Export DB cache as YAML for unit tests."""

import sys
import yaml

from vmaas.webapp.cache import Cache  # pylint: disable=C0413


class YamlCache(Cache):
    """YamlCache class. Dump dictionaries from Cache in YAML format."""

    def __init__(self, filename):  # pylint: disable=W0231
        """Override Cache.__init__, avoid calling Cache.reload()"""
        self.filename = filename
        self.clear()

    def load_yaml(self):
        """Load cache from YAML file."""
        with open(self.filename, "r", encoding='utf8') as stream:
            try:
                # FIXME: workaround using UnsafeLoader because https://github.com/yaml/pyyaml/issues/380
                data = yaml.load(stream, Loader=yaml.UnsafeLoader)
            except yaml.YAMLError as err:
                print(err)

        for key, val in data.items():
            setattr(self, key, val)
        self.build_indexes()
        return self

    def dump(self, output):
        """Dump YAML with all dictionaries."""
        attrs = vars(self)
        del attrs["filename"]

        with open(output, "w", encoding='utf8') as file:
            yaml.dump(attrs, file)


def load_test_cache():
    """Load cache with testing data."""
    cache = YamlCache("test/data/cache.yml")
    return cache.load_yaml()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:\n./yaml_cache.py <vmaas.dbm path> <yaml output>")
        sys.exit(1)

    CACHE = YamlCache(filename=sys.argv[1])
    CACHE.dump(output=sys.argv[2])
