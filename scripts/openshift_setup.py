#!/usr/bin/python
"""
This is a setup script to set various attributes to OpenShift objects.
Script takes YAML produced by kompose tool, sets various attributes and prints final YAML.
(this needs to be done because of missing features in kompose tool)
"""

import os
import sys
import yaml

WEBSOCKET_URL_KEY_NAME = "REPOSCAN_WEBSOCKET_URL"
POSTGRESQL_HOST_KEY_NAME = "POSTGRESQL_HOST"
REPOSCAN_HOST_KEY_NAME = "REPOSCAN_HOST"


def get_env_opts():
    """Override default settings from environment."""
    options = {}
    options["app_name"] = os.getenv("app_name", "vmaas")
    options["app_id"] = os.getenv("app_id", "")
    options["storage_size"] = {}
    options["storage_size"]["vmaas-db-data"] = os.getenv("storage_size_db", "5Gi")
    options["storage_size"]["vmaas-reposcan-tmp"] = os.getenv("storage_size_tmp", "15Gi")
    options["storage_size"]["vmaas-dump-data"] = os.getenv("storage_size_dump", "5Gi")
    options["healthchecks"] = {}
    options["healthchecks"]["webapp"] = {"vmaas-webapp": os.getenv("webapp_healthchecks_path" ,"./healthchecks/webapp.yml")}
    options["healthchecks"]["reposcan"] = {"vmaas-reposcan": os.getenv("reposcan_healthchecks_path" ,"./healthchecks/reposcan.yml")}
    options["healthchecks"]["database"] = {"vmaas-database": os.getenv("database_healthchecks_path" ,"./healthchecks/database.yml")}
    options["healthchecks"]["apidoc"] = {"vmaas-apidoc": os.getenv("apidoc_healthchecks_path" ,"./healthchecks/apidoc.yml")}
    return options


def set_app_label(options, item):
    """Set application label."""
    item["metadata"]["labels"]["app"] = options["app_name"]


def _append_to_value(data_dict, key, suffix):
    current_value = data_dict.get(key, None)
    if current_value is not None:
        data_dict[key] = "%s-%s" % (current_value, suffix)


def set_app_id(options, item):
    """Set application id to all components."""
    if options["app_id"]:
        # Append to name
        _append_to_value(item["metadata"], "name", options["app_id"])
        # Append to service label
        _append_to_value(item["metadata"]["labels"], "io.kompose.service", options["app_id"])
        # Append to service selector
        if item["kind"] == "Service":
            _append_to_value(item["spec"]["selector"], "io.kompose.service", options["app_id"])
        # Update URLs in config
        elif item["kind"] == "ConfigMap":
            if WEBSOCKET_URL_KEY_NAME in item["data"]:
                item["data"][WEBSOCKET_URL_KEY_NAME] = item["data"][WEBSOCKET_URL_KEY_NAME].replace(
                    "reposcan", "reposcan-%s" % options["app_id"])
            for key in (POSTGRESQL_HOST_KEY_NAME, REPOSCAN_HOST_KEY_NAME):
                if key in item["data"]:
                    item["data"][key] = "%s-%s" % (item["data"][key], options["app_id"])
        # Append to deployment config attributes
        elif item["kind"] == "DeploymentConfig":
            _append_to_value(item["metadata"]["labels"], "app", options["app_id"])
            _append_to_value(item["spec"]["selector"], "io.kompose.service", options["app_id"])
            _append_to_value(item["spec"]["template"]["metadata"]["labels"], "io.kompose.service", options["app_id"])
            for container in item["spec"]["template"]["spec"]["containers"]:
                for env_var in container.get("env", []):
                    if "valueFrom" in env_var and "configMapKeyRef" in env_var["valueFrom"]:
                        _append_to_value(env_var["valueFrom"]["configMapKeyRef"], "name", options["app_id"])
                for mount in container.get("volumeMounts", []):
                    _append_to_value(mount, "name", options["app_id"])
            for volume in item["spec"]["template"]["spec"].get("volumes", []):
                _append_to_value(volume, "name", options["app_id"])
                if "persistentVolumeClaim" in volume:
                    _append_to_value(volume["persistentVolumeClaim"], "claimName", options["app_id"])
            for image_change_trigger in [trigger for trigger in item["spec"]["triggers"]
                                         if trigger["type"] == "ImageChange"]:
                original_name = image_change_trigger["imageChangeParams"]["from"]["name"]
                image_name_tag = original_name.split(":")
                image_change_trigger["imageChangeParams"]["from"]["name"] = "%s-%s:%s" % (
                    image_name_tag[0], options["app_id"], image_name_tag[1])


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
            # append app_id as a suffix to all objects
            set_app_id(options, item)
            processed_items[(kind, name)] = item
    data["items"] = list(processed_items.values())
    print(yaml.dump(data))

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage: cat OpenShiftObjects.yml | app_name=\"vmaas\" %s > PreparedOpenShiftObjects.yml" %
              sys.argv[0])
        sys.exit(1)
    main()
