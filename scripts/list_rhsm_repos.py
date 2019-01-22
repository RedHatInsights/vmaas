#!/usr/bin/python3

import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import json
import requests

CONFIG_FILE = os.environ['HOME'] + "/.list_rhsm_repos.json"
CONFIG_OPTIONS = ["ENG_PRODUCT_API", "ENG_PRODUCT_API_CERT", "ENG_PRODUCT_API_KEY",
                  "PULP_API", "PULP_USER", "PULP_PASSWORD"]
RHSM_CA_CERT = "/etc/rhsm/ca/redhat-uep.pem"
VMAAS_ENTITLEMENT_NAME = "RHSM-CDN"
EXAMPLE_TEXT = """usage:
  %(progname)s -l --show-content-sets
    prints products and content sets in human readable form
  %(progname)s --rhsm-cert=/path/to/entitlement/cert.pem
    prints JSON request for reposcan containing all products and content sets
  %(progname)s --rhsm-cert=/path/to/entitlement/cert.pem -i 69
    prints JSON request for reposcan containing only 'RHEL Server' product and its content sets
""" % {"progname": sys.argv[0]}


def parse_config_file():
    if not os.path.isfile(CONFIG_FILE):
        print("Config file %s not found." % CONFIG_FILE)
        sys.exit(1)

    with open(CONFIG_FILE, "r") as fp:
        options = json.load(fp)

    for option in CONFIG_OPTIONS:
        if option not in options:
            print("Undefined config option: %s" % option)
            sys.exit(1)

    return options


def get_eng_products_response(options):
    active_eng_products_headers = {"content-type": "application/json",
                                   "accept": "application/json"}
    active_eng_products_payload = {"criteria": [{"field": "status", "stringValues": ["ACTIVE"]}],
                                   "retrieveInactives": False, "retrieveAttributes": False}
    active_eng_products_url = options["ENG_PRODUCT_API"]
    eng_products_cert = options["ENG_PRODUCT_API_CERT"]
    eng_products_key = options["ENG_PRODUCT_API_KEY"]
    return requests.post(active_eng_products_url, data=json.dumps(active_eng_products_payload),
                         headers=active_eng_products_headers, cert=(eng_products_cert, eng_products_key))


def get_pulp_repos_response(options):
    pulp_repos_headers = {"content-type": "application/json",
                          "accept": "application/json"}
    pulp_repos_url = options["PULP_API"]
    return requests.get(pulp_repos_url, headers=pulp_repos_headers,
                        auth=(options["PULP_USER"], options["PULP_PASSWORD"]))


def get_eng_products():
    eng_products_response = get_eng_products_response(options)
    eng_products_tuples = []
    eng_products_content = {}
    cs_label_to_url = {}
    if eng_products_response.status_code == 200:
        data = json.loads(eng_products_response.text)
        for product in data["products"]:
            # Is there any SKU associated?
            if product["skus"] or args.include_no_skus:
                eng_product_id = int(product["oid"])
                # Filtering
                if (args.include_products and str(eng_product_id) not in args.include_products) or \
                        (args.exclude_products and str(eng_product_id) in args.exclude_products):
                    continue
                eng_products_tuples.append((eng_product_id, product["name"]))
                eng_products_content[eng_product_id] = set()
                for content in product["content"]:
                    if content["type"] == "YUM":
                        if not content["contentUrl"].endswith("SRPMS") or args.include_sources:
                            eng_products_content[eng_product_id].add((content["label"], content["name"],
                                                                      content["contentUrl"]))
                            cs_label_to_url[content["label"]] = content["contentUrl"]
    else:
        sys.stderr.write("HTTP error occurred: %d\n" % eng_products_response.status_code)
        sys.exit(2)

    return eng_products_tuples, eng_products_content, cs_label_to_url


def get_pulp_repos(cs_label_to_url):
    arches_by_content_set = {}
    releasevers_by_content_set = {}
    pulp_repos_response = get_pulp_repos_response(options)
    if pulp_repos_response.status_code == 200:
        data = json.loads(pulp_repos_response.text)
        for r in data:
            if r["notes"]["_repo-type"] == "rpm-repo" and "relative_url" in r["notes"]:
                content_set = r["notes"]["content_set"]
                # Path with variables
                base_url = cs_label_to_url.get(content_set, None)
                if base_url is None:
                    continue
                # Path without variables
                relative_url = r["notes"]["relative_url"]
                if not relative_url.startswith("/"):
                    relative_url = "/%s" % relative_url
                base_url_parts = base_url.split("/")
                relative_url_parts = relative_url.split("/")
                # Compare urls with variables and without and extract releasevers and basearches
                for idx, part in enumerate(base_url_parts):
                    if part == "$releasever":
                        releasevers_by_content_set.setdefault(content_set, set()).add(relative_url_parts[idx])
                    elif part == "$basearch":
                        arches_by_content_set.setdefault(content_set, set()).add(relative_url_parts[idx])
    else:
        sys.stderr.write("HTTP error occurred: %d\n" % pulp_repos_response.status_code)
        sys.exit(2)

    return arches_by_content_set, releasevers_by_content_set


def read_cert_content(file_name):
    with open(file_name, "r") as file:
        content = file.read()
        return content


def get_certs(args):
    ca_cert = read_cert_content(RHSM_CA_CERT)
    client_cert = read_cert_content(args.rhsm_cert)
    if args.rhsm_key:
        client_key = read_cert_content(args.rhsm_key)
    else:
        client_key = ""
    return ca_cert, client_cert, client_key


if __name__ == '__main__':
    parser = ArgumentParser(epilog=EXAMPLE_TEXT, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-l", "--list-products", action="store_true",
                        help="List active engineering products in console.")
    parser.add_argument("--show-content-sets", action="store_true",
                        help="Show content sets provided by products. Use only with -l.")
    parser.add_argument("--include-no-skus", action="store_true", help="Include products without SKUs in output.")
    parser.add_argument("--include-sources", action="store_true", help="Include source content sets in output.")
    parser.add_argument("-i", "--include-products", action="append", help="Include product IDs only.")
    parser.add_argument("-e", "--exclude-products", action="append", help="Exclude product IDs.")
    parser.add_argument("--rhsm-cert", action="store", help="Path to RHSM client certificate.")
    parser.add_argument("--rhsm-key", action="store", help="Path to RHSM client key (can be included in cert file).")
    parser.add_argument("--cdn-url", action="store", help="CDN mirror to use.", default="https://cdn.redhat.com")
    args = parser.parse_args()
    options = parse_config_file()

    # Require RHSM client certificate if producing target JSON request
    if not args.list_products and (not args.rhsm_cert or not os.path.isfile(args.rhsm_cert)):
        print("Please specify RHSM client certificate!")
        sys.exit(3)

    eng_products_tuples, eng_products_content, cs_label_to_url = get_eng_products()
    arches_by_content_set, releasevers_by_content_set = get_pulp_repos(cs_label_to_url)

    # List in human readable list
    if args.list_products:
        for eng_product_id, product_name in sorted(eng_products_tuples, key=lambda item: item[0]):
            print("%s %s" % (eng_product_id, product_name))
            if args.show_content_sets:
                for cs_label, _, cs_url in sorted(eng_products_content[eng_product_id]):
                    print("    %s %s arches:%s releasevers:%s" % (cs_label, cs_url,
                                                                  ",".join(arches_by_content_set.get(
                                                                      cs_label, set())),
                                                                  ",".join(releasevers_by_content_set.get(
                                                                      cs_label, set()))))
    # List as JSON request for reposcan
    else:
        ca_cert, client_cert, client_key = get_certs(args)
        output_dict = {"entitlement_cert": {"name": VMAAS_ENTITLEMENT_NAME,
                                            "ca_cert": ca_cert,
                                            "cert": client_cert,
                                            "key": client_key},
                       "products": {}}
        for eng_product_id, product_name in sorted(eng_products_tuples, key=lambda item: item[0]):
            # Are there any CS?
            if eng_products_content[eng_product_id]:
                output_dict["products"][product_name] = {"redhat_eng_product_id": eng_product_id,
                                                         "content_sets": {}}
                for cs_label, cs_name, cs_url in sorted(eng_products_content[eng_product_id]):
                    output_dict["products"][product_name]["content_sets"][cs_label] = {
                        "name": cs_name,
                        "baseurl": "%s%s" % (args.cdn_url, cs_url),
                        "basearch": list(arches_by_content_set.get(cs_label, set())),
                        "releasever": list(releasevers_by_content_set.get(cs_label, set()))
                    }
        print(json.dumps([output_dict]))
