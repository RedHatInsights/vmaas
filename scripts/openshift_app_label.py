#!/usr/bin/python
"""
This script is a workaround to set app label to categorize OpenShift objects.
Script takes YAML produced by kompose tool, sets app label for items and prints final YAML.
(kompose 1.7.0 doesn't support setting this label natively)
"""

import sys
import yaml


def main():
    """Main function."""
    input_text = sys.stdin.read()
    app_name = sys.argv[1]
    data = yaml.load(input_text)
    for item in data["items"]:
        if "metadata" in item and "labels" in item["metadata"]:
            item["metadata"]["labels"]["app"] = app_name
    print(yaml.dump(data))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: cat OpenShiftObjects.yml | %s appName > AppOpenShiftObjects.yml" %
              sys.argv[0])
        sys.exit(1)
    main()
