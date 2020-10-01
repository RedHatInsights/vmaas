#!/usr/bin/env python3

import yaml
import json
import os
import sys

class Error:

    def __init__(self, msg, f):
        self.msg = msg
        self.f = f

    def __repr__(self):
        return "ERROR %s: %s" % (self.f, self.msg)

def validate(f):
    print("Validating %s" % f)
    if not f.endswith(".yaml") and not f.endswith(".yml"):
        yield Error("Bad file name", f)
        return

    try:
        with open(f) as fp:
            y = yaml.safe_load(fp)

        if not y["metadata"]["name"]:
            yield Error("Resource name not found", f)

        d = y["data"]

        if len(d) != 1:
            yield Error("Invalid number of keys in ConfigMap", f)
        
        key = list(d.keys())[0]

        if not key.endswith(".json"):
            yield Error("Key does not end with .json: %s" % key, f)

        json.loads(d[key])
    except Exception as e:
        yield Error(e.msg, f)

seen_error = False

for f in os.listdir(sys.argv[1]):
    for err in validate(sys.argv[1] + f):
        seen_error = True
        print(err)

if seen_error:
    sys.exit(1)
