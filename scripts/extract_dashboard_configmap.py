#!/usr/bin/env python3

import json
import sys
import yaml

with open(sys.argv[1]) as fp:
    y = yaml.safe_load(fp)
    d = y["data"]
    key = list(d.keys())[0]
    dashboard = json.loads(d[key])
    print(json.dumps(dashboard, indent=4, sort_keys=True))
