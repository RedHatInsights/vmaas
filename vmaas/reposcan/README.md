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
    "Red Hat Enterprise Linux Server": {
      "redhat_eng_product_id": 69,
      "content_sets": {
        "rhel-7-server-rpms": {
          "name": "Red Hat Enterprise Linux 7 Server (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/server/7/$releasever/$basearch/os/",
          "basearch": ["x86_64"],
          "releasever": ["7Server", "7.4"]
        },
        "rhel-7-server-optional-rpms": {
          "name": "Red Hat Enterprise Linux 7 Server - Optional (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/server/7/$releasever/$basearch/optional/os/",
          "basearch": ["x86_64"],
          "releasever": ["7Server", "7.4"]
        },
        "rhel-6-server-rpms": {
          "name": "Red Hat Enterprise Linux 6 Server (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/server/6/$releasever/$basearch/os/",
          "basearch": ["x86_64"],
          "releasever": ["6Server", "6.9"]
        },
        "rhel-6-server-optional-rpms": {
          "name": "Red Hat Enterprise Linux 6 Server - Optional (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/server/6/$releasever/$basearch/optional/os/",
          "basearch": ["x86_64"],
          "releasever": ["6Server", "6.9"]
        }
      }
    },
    "Red Hat Enterprise Linux Workstation": {
      "redhat_eng_product_id": 71,
      "content_sets": {
        "rhel-7-workstation-rpms": {
          "name": "Red Hat Enterprise Linux 7 Workstation (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/workstation/7/$releasever/$basearch/os/",
          "basearch": ["x86_64"],
          "releasever": ["7Workstation", "7.4"]
        },
        "rhel-7-workstation-optional-rpms": {
          "name": "Red Hat Enterprise Linux 7 Workstation - Optional (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/workstation/7/$releasever/$basearch/optional/os/",
          "basearch": ["x86_64"],
          "releasever": ["7Workstation", "7.4"]
        },
        "rhel-6-workstation-rpms": {
          "name": "Red Hat Enterprise Linux 6 Workstation (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/workstation/6/$releasever/$basearch/os/",
          "basearch": ["x86_64"],
          "releasever": ["6Workstation", "6.9"]
        },
        "rhel-6-workstation-optional-rpms": {
          "name": "Red Hat Enterprise Linux 6 Workstation - Optional (RPMs)",
          "baseurl": "https://cdn.redhat.com/content/dist/rhel/workstation/6/$releasever/$basearch/optional/os/",
          "basearch": ["x86_64"],
          "releasever": ["6Workstation", "6.9"]
        }
      }
    }
  }
},
{
  "products": {
    "Fedora": {
      "content_sets": {
        "updates": {
          "name": "Fedora Updates",
          "baseurl": "https://mirrors.nic.cz/fedora/linux/updates/$releasever/$basearch/",
          "basearch": ["x86_64"],
          "releasever": ["27"]
        }
      }
    }
  }
}]
```

Repositories can be grouped and optionally have entitlement certificate specified.

Example commands:

`$ curl -d @repolist.json -X POST http://127.0.0.1:8081/api/v1/sync/repo`

`$ curl -X GET http://127.0.0.1:8081/api/v1/sync/repo`

`$ curl -X GET http://127.0.0.1:8081/api/v1/sync/cve`

`$ curl -X GET http://127.0.0.1:8081/api/v1/sync`

This allows to control the reposcan container manually.


