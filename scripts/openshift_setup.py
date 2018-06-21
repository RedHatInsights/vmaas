#!/usr/bin/python
"""
This is a setup script to set various attributes to OpenShift objects.
Script takes YAML produced by kompose tool, sets various attributes and prints final YAML.
(this needs to be done because of missing features in kompose tool)
"""

import os
import sys
import yaml


def get_env_opts():
    """Override default settings from environment."""
    options = {}
    options["app_name"] = os.getenv("app_name", "vmaas")
    options["storage_size"] = {}
    options["storage_size"]["vmaas-db-data"] = os.getenv("storage_size_db", "5Gi")
    options["storage_size"]["vmaas-reposcan-tmp"] = os.getenv("storage_size_tmp", "15Gi")
    options["storage_size"]["vmaas-dump-data"] = os.getenv("storage_size_dump", "5Gi")
    options["healthchecks"] = {}
    options["healthchecks"]["webapp"] = {"vmaas-webapp": os.getenv("webapp_healthchecks_path" ,"./healthchecks/webapp.yml")}
    options["healthchecks"]["reposcan"] = {"vmaas-reposcan": os.getenv("reposcan_healthchecks_path" ,"./healthchecks/reposcan.yml")}
    options["healthchecks"]["database"] = {"vmaas-database": os.getenv("database_healthchecks_path" ,"./healthchecks/database.yml")}
    return options


def set_app_label(options, item):
    """Set application label."""
    item["metadata"]["labels"]["app"] = options["app_name"]


def set_storage_attributes(options, name, item):
    """Set storage sizes."""
    if name in options["storage_size"]:
        item["spec"]["resources"]["requests"]["storage"] = options["storage_size"][name]


def add_health_checks(options, name, item):
    """Add health checks."""
    if name in options["healthchecks"]:
        for container in item["spec"]["template"]["spec"]["containers"]:
            container_name = container["name"]
            if container_name in options["healthchecks"][name]:
                file_path = options["healthchecks"][name][container_name]
                with open(file_path, "r") as healthcheck_file:
                    healthcheck_yaml = yaml.load(healthcheck_file)
                    for probe_type, probe in healthcheck_yaml.items():
                        container[probe_type] = probe


def main():
    """Main function."""
    options = get_env_opts()
    input_text = sys.stdin.read()
    data = yaml.load(input_text)
    processed_items = {}
    for item in data["items"]:
        kind = item["kind"]
        name = item["metadata"]["name"]
        if (kind, name) not in processed_items:
            if kind == "DeploymentConfig":
                set_app_label(options, item)
                add_health_checks(options, name, item)
            elif kind == "PersistentVolumeClaim":
                # set required storage size, kompose supports only to set this on service level - all volumes
                # linked to service have same size
                set_storage_attributes(options, name, item)
            processed_items[(kind, name)] = item
    data["items"] = list(processed_items.values())
    print(yaml.dump(data))

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage: cat OpenShiftObjects.yml | app_name=\"vmaas\" %s > PreparedOpenShiftObjects.yml" %
              sys.argv[0])
        sys.exit(1)
    main()
