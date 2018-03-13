# VMaaS Database population tool

### Build a new image:

```docker build -t vmaas_reposcan_img .```

### Create a container

```docker create -it -p 8081:8081 --link vmaas_db_ctr:database --name vmaas_reposcan_ctr vmaas_reposcan_img```

### Start a container:

```docker start vmaas_reposcan_ctr```

### Run bash in container:

```docker exec -it vmaas_reposcan_ctr bash```


### `reposcan` service API:

It's possible to manage this container during it's lifespan. There are following API endpoints:

- **/api/v1/sync/repo**
  - _GET_ - Synces all repositories previously synced into DB
  - _POST_ - Synces repositories provided in attached JSON list
- **/api/v1/sync/cve**
  - _GET_ - Synces all CVEs.

There is a limit to single worker to prevent DB conflicts when importing. When user calls any of these sync API while any other sync job is already running, this request will get refused.

JSON list of repositories have following format:
```json
[{
  "entitlement_cert": {
    "name": "RHSM-CDN",
    "ca_cert": "<CA CERTIFICATE>",
    "cert": "<CLIENT CERTIFICATE>",
    "key": "<CLIENT KEY>"
  },
  "products": {
    "69": {
      "name": "Red Hat Enterprise Linux Server",
      "content_sets": {
        "rhel-7-server-rpms": {
          "name": "Red Hat Enterprise Linux 7 Server (RPMs)",
          "repos": {
            "rhel-7-server-rpms__7Server__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/7/7Server/x86_64/os/",
            "rhel-7-server-rpms__7_DOT_4__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/7/7.4/x86_64/os/"
          }
        },
        "rhel-7-server-optional-rpms": {
          "name": "Red Hat Enterprise Linux 7 Server - Optional (RPMs)",
          "repos": {
            "rhel-7-server-optional-rpms__7Server__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/7/7Server/x86_64/optional/os/",
            "rhel-7-server-optional-rpms__7_DOT_4__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/7/7.4/x86_64/optional/os/"
          }
        },
        "rhel-6-server-rpms": {
          "name": "Red Hat Enterprise Linux 6 Server (RPMs)",
          "repos": {
            "rhel-6-server-rpms__6Server__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/6/6Server/x86_64/os/",
            "rhel-6-server-rpms__6_DOT_9__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/6/6.9/x86_64/os/"
          }
        },
        "rhel-6-server-optional-rpms": {
          "name": "Red Hat Enterprise Linux 6 Server - Optional (RPMs)",
          "repos": {
            "rhel-6-server-optional-rpms__6Server__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/6/6Server/x86_64/optional/os/",
            "rhel-6-server-optional-rpms__6_DOT_9__x86_64": "https://cdn.redhat.com/content/dist/rhel/server/6/6.9/x86_64/optional/os/"
          }
        }
      }
    },
    "71": {
      "name": "Red Hat Enterprise Linux Workstation",
      "content_sets": {
        "rhel-7-workstation-rpms": {
          "name": "Red Hat Enterprise Linux 7 Workstation (RPMs)",
          "repos": {
            "rhel-7-workstation-rpms__7Workstation__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/7/7Workstation/x86_64/os/",
            "rhel-7-workstation-rpms__7_DOT_4__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/7/7.4/x86_64/os/"
          }
        },
        "rhel-7-workstation-optional-rpms": {
          "name": "Red Hat Enterprise Linux 7 Workstation - Optional (RPMs)",
          "repos": {
            "rhel-7-workstation-optional-rpms__7Workstation__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/7/7Workstation/x86_64/optional/os/",
            "rhel-7-workstation-optional-rpms__7_DOT_4__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/7/7.4/x86_64/optional/os/"
          }
        },
        "rhel-6-workstation-rpms": {
          "name": "Red Hat Enterprise Linux 6 Workstation (RPMs)",
          "repos": {
            "rhel-6-workstation-rpms__6Workstation__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/6/6Workstation/x86_64/os/",
            "rhel-6-workstation-rpms__6_DOT_9__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/6/6.9/x86_64/os/"
          }
        },
        "rhel-6-workstation-optional-rpms": {
          "name": "Red Hat Enterprise Linux 6 Workstation - Optional (RPMs)",
          "repos": {
            "rhel-6-workstation-optional-rpms__6Workstation__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/6/6Workstation/x86_64/optional/os/",
            "rhel-6-workstation-optional-rpms__6_DOT_9__x86_64": "https://cdn.redhat.com/content/dist/rhel/workstation/6/6.9/x86_64/optional/os/"
          }
        }
      }
    }
  }
},
{
  "repos": {
    "fedora-26-updates": "https://mirrors.nic.cz/fedora/linux/updates/26/x86_64/",
    "fedora-27-updates": "https://mirrors.nic.cz/fedora/linux/updates/27/x86_64/"
  }
}]
```

Repositories can be grouped and optionally have entitlement certificate specified.

Example commands:

`$ curl -d @repolist.json -X POST http://127.0.0.1:8081/api/v1/sync/repo`

`$ curl -X GET http://127.0.0.1:8081/api/v1/sync/repo`

`$ curl -X GET http://127.0.0.1:8081/api/v1/sync/cve`

This allows to control the reposcan container manually.


