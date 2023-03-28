# Changelog

<!--next-version-placeholder-->

## v2.41.1 (2023-03-28)
### Fix
* Docker-compose build ([`25e44da`](https://github.com/RedHatInsights/vmaas/commit/25e44da7856cb52960dc492c0a14ffcbb1482ef2))
* Handle exception when sending slack notification ([`7379d2a`](https://github.com/RedHatInsights/vmaas/commit/7379d2ae7a59dbf69373e0c6b3ffe9bb8f986201))

## v2.41.0 (2023-03-27)
### Feature
* **webapp:** Use timer instead of websocket to refresh data ([`4e14fa7`](https://github.com/RedHatInsights/vmaas/commit/4e14fa7db8511b4a09238ea6ca2b487f9dcebc2a))

## v2.40.0 (2023-03-14)
### Feature
* **fedramp:** Use tls for outgoing connections and simplify config ([`e3e9e71`](https://github.com/RedHatInsights/vmaas/commit/e3e9e719bb97b4f904e45af14d6d8b5b5a7281fb))

### Fix
* **fedramp:** Set tls ca for dump download ([`7d27e62`](https://github.com/RedHatInsights/vmaas/commit/7d27e620206c54e5b4f10cce6ffc0f84effe1f42))

## v2.39.3 (2023-02-17)
### Fix
* **vmaas-go:** Incorrect json field for third_party updates ([`eb39dba`](https://github.com/RedHatInsights/vmaas/commit/eb39dba5f82f97135085b4ca11af637f37e7daef))
* **vmaas-go:** Return errata: [] instead of null ([`23908a8`](https://github.com/RedHatInsights/vmaas/commit/23908a8f96282377c3751ae8ff8acb34b0875572))
* **vmaas-go:** Panic during refresh ([`5d2f900`](https://github.com/RedHatInsights/vmaas/commit/5d2f9001de52e89af17e698c14c0ec8a7dc53312))

## v2.39.2 (2023-01-23)
### Fix
* Inconsistent response for invalid packages ([`cdf3f48`](https://github.com/RedHatInsights/vmaas/commit/cdf3f488174c9a10ae65e1cc6b0c18fdc33475a8))

## v2.39.1 (2023-01-20)
### Fix
* Allow null repository_list ([`0dc8546`](https://github.com/RedHatInsights/vmaas/commit/0dc8546191054bec26832c2338829226789406f4))

## v2.39.0 (2023-01-13)
### Feature
* **vmaas-go:** Use goroutines ([`6859dca`](https://github.com/RedHatInsights/vmaas/commit/6859dca4da5863c528d68494cdd07de3e4e8f639))

## v2.38.2 (2023-01-10)
### Fix
* Watchtower params ([`02ccf10`](https://github.com/RedHatInsights/vmaas/commit/02ccf1026592dfc42b1a0b763fcfb9667d0e04cb))

## v2.38.1 (2023-01-09)
### Fix
* **vmaas-go:** Incorrect cve-errata mapping ([`56094cf`](https://github.com/RedHatInsights/vmaas/commit/56094cffee0ffaff4b4e7218af51a03b69f9f2d6))

## v2.38.0 (2023-01-09)
### Feature
* Use ubi9, python3.9, go1.18 ([`c3e3b60`](https://github.com/RedHatInsights/vmaas/commit/c3e3b602fc8c6731bed14550cde967c5287cb495))

## v2.37.11 (2023-01-05)
### Fix
* **vmaas-go:** Cache reload, adjust GOGC ([`3ab6317`](https://github.com/RedHatInsights/vmaas/commit/3ab6317ef2c2f5547729f78553adf897fa9d46f3))

## v2.37.10 (2022-12-19)
### Fix
* **vmaas-go:** Update vmaas-lib and set GC ([`6572ef5`](https://github.com/RedHatInsights/vmaas/commit/6572ef513ae21f909cdbc0109f54c57d85b2306c))

## v2.37.9 (2022-12-15)
### Fix
* **vmaas-go:** Optimizations ([`8d2639c`](https://github.com/RedHatInsights/vmaas/commit/8d2639cda988217648216d6aff5421a92fdd1131))

## v2.37.8 (2022-12-12)
### Fix
* **vmaas-go:** Updates when releasever in repo is empty ([`80c86c0`](https://github.com/RedHatInsights/vmaas/commit/80c86c0fa5e41a4b8a3e6333a2b7328812f5818d))

## v2.37.7 (2022-12-08)
### Fix
* **vmaas-go:** Bump vmaas-lib version to fix arch compatibility ([`ecbd93a`](https://github.com/RedHatInsights/vmaas/commit/ecbd93a022662f0d79e1bf4edfe0cb2868cb231f))

## v2.37.6 (2022-12-08)
### Fix
* **vmaas-go:** Add metrics ([`daf67c0`](https://github.com/RedHatInsights/vmaas/commit/daf67c0c6731b7bcb17f2d3952b50faa9776b8df))

## v2.37.5 (2022-12-07)
### Fix
* **vmaas-go:** Recover from panic and respond 500 ([`09be0db`](https://github.com/RedHatInsights/vmaas/commit/09be0db507bf35ad9a32241beb9ae47e820858eb))

## v2.37.4 (2022-11-25)
### Fix
* **vmaas-go:** Don't proxy request when error is present ([`6c86060`](https://github.com/RedHatInsights/vmaas/commit/6c86060465d95830b866e405bcdb5b5aa719a93e))

## v2.37.3 (2022-11-25)
### Fix
* **vmaas-go:** Return 503 during cache reload ([`6913cc9`](https://github.com/RedHatInsights/vmaas/commit/6913cc9b7a734db169c063c3d9bbe68d0a44d412))

## v2.37.2 (2022-11-24)
### Fix
* Define cpu/memory limit/requests separately ([`22a96d9`](https://github.com/RedHatInsights/vmaas/commit/22a96d96015a1d3a0d7ece3d317a3a333a35852d))

## v2.37.1 (2022-11-23)
### Fix
* **probes:** Define custom probes ([`7a5c438`](https://github.com/RedHatInsights/vmaas/commit/7a5c4384f4f5e811cfb263817d9ec328869a4179))

## v2.37.0 (2022-11-22)
### Feature
* **vulnerabilities:** Vulns by repository_paths ([`985ad04`](https://github.com/RedHatInsights/vmaas/commit/985ad04c243e9569b46327813f567cdb303dd087))
* **updates:** Look up updates by repository paths ([`5ce94f0`](https://github.com/RedHatInsights/vmaas/commit/5ce94f082c29d9bb64025d65be2f39a12622c7b2))
* **cache:** Repository id by path ([`47bc078`](https://github.com/RedHatInsights/vmaas/commit/47bc07893f90d352dd8cb2be2f974eba123ba70e))

### Fix
* **updates:** Repository_paths used alone ([`2cac2b4`](https://github.com/RedHatInsights/vmaas/commit/2cac2b4a28f00cba3f9d01f11e568e3327c4636a))

## v2.36.0 (2022-11-22)
### Feature
* **webapp-go:** Build and deployment ([`5ab7743`](https://github.com/RedHatInsights/vmaas/commit/5ab7743bd8a3d289d0d4e14a5b9e5a1adf62c137))
* **webapp-go:** Local config ([`b01edf3`](https://github.com/RedHatInsights/vmaas/commit/b01edf39917cc917771c54be8299311c7f11639b))
* **webapp-go:** App handling updates and vulnerabilities ([`c7436c1`](https://github.com/RedHatInsights/vmaas/commit/c7436c1b2e54b5c204116a711c611e05ab5f3fb2))
* **webapp-go:** Base and utils based on redhatinsights/patchman-engine ([`133b098`](https://github.com/RedHatInsights/vmaas/commit/133b098c1f124ff0d5d812a6772fe397259ad736))

## v2.35.4 (2022-11-14)
### Fix
* **tests:** Test env vars unqoted ([`4800058`](https://github.com/RedHatInsights/vmaas/commit/4800058fcbdfdae4d15049602d10905fcf9a62d4))
* **tests:** Skip unrelated pipenv check ([`bfe0a7b`](https://github.com/RedHatInsights/vmaas/commit/bfe0a7ba750db0ba4e323e96fa362530e7dbee0b))

## v2.35.3 (2022-10-07)
### Fix
* **reposcan:** Collect prometheus metrics from child processes ([`4c16942`](https://github.com/RedHatInsights/vmaas/commit/4c16942abe5817c5a479d46f14d0ec7805d15afd))

## v2.35.2 (2022-07-19)
### Fix
* Run flake8 in GH actions and fix flake8 issues ([`ca6d8c1`](https://github.com/RedHatInsights/vmaas/commit/ca6d8c1782a2122a028f247078ab35257c9ab7c9))

## v2.35.1 (2022-05-30)
### Fix
* Rename epel repo to epel-8 ([`7b13602`](https://github.com/RedHatInsights/vmaas/commit/7b1360265a1eeba3e35c419b40318d48546138e7))

## v2.35.0 (2022-03-07)
### Feature
* **webapp:** Strip prefixes from repository names ([`bcd2572`](https://github.com/RedHatInsights/vmaas/commit/bcd2572de2b192a1b98a8e5b4de91ea7d74b2c87))

## v2.34.6 (2022-03-02)
### Fix
* **reposcan:** Fix lint in test_patchlist.py ([`b71de25`](https://github.com/RedHatInsights/vmaas/commit/b71de25e43286e5d39270b70af6844a4d2e42160))

## v2.34.5 (2022-03-01)
### Fix
* **reposcan:** Handle all other sync exceptions to not skip syncing valid repos ([`9d355da`](https://github.com/RedHatInsights/vmaas/commit/9d355da4f13585c3d9a50ff1220a0e252011cf83))

## v2.34.4 (2022-02-22)
### Fix
* **local-deployment:** Official PostgreSQL container has different mount path ([`9fcc693`](https://github.com/RedHatInsights/vmaas/commit/9fcc69332f5bd91189e2918eb86fc1dc534bd331))

## v2.34.3 (2022-02-14)
### Fix
* **reposcan:** EUS repos are mapped to CPEs of incorrect EUS version ([`f9fc5da`](https://github.com/RedHatInsights/vmaas/commit/f9fc5da8b88011bf80637c30131e66598ac2a40e))

## v2.34.2 (2022-02-07)
### Fix
* **webapp:** In errata_associated CVE list include also CVEs found only in OVAL files (missing in repodata due to error) ([`4b0157e`](https://github.com/RedHatInsights/vmaas/commit/4b0157ef9994931d16549659efae80339c8c02cd))
* **reposcan:** Don't delete whole CS when want to delete only repo with null basearch and releasever ([`862c2cb`](https://github.com/RedHatInsights/vmaas/commit/862c2cb67a7a2fd74eed1f86a60d40ff0bb8681d))

## v2.34.1 (2022-02-02)
### Fix
* **reposcan:** Allow redirects ([`dc433c8`](https://github.com/RedHatInsights/vmaas/commit/dc433c861551b34aec2a2713118fd12c2fefebc7))

## v2.34.0 (2022-01-25)
### Feature
* **reposcan:** Delete all repos removed from list ([`e9ec3a8`](https://github.com/RedHatInsights/vmaas/commit/e9ec3a81bb08595a8d3d17168c0b1b26ca5aacfc))

## v2.33.1 (2022-01-21)
### Fix
* **webapp:** Remove null probes in clowaddp.yaml ([`5e38b8d`](https://github.com/RedHatInsights/vmaas/commit/5e38b8dd703fc453285c0d7b36dcc9ff2ee0da19))

## v2.33.0 (2022-01-18)
### Feature
* **webapp:** Use CPE-repository mapping if available ([`9e06241`](https://github.com/RedHatInsights/vmaas/commit/9e06241f5b3ac8fb28672154739a7a3afc71380d))
* **reposcan:** Link CPEs with specific repos, not only content sets ([`428bfad`](https://github.com/RedHatInsights/vmaas/commit/428bfad8e974ae0b0107d7fd557fb842f9b333aa))

## v2.32.11 (2022-01-10)
### Fix
* **reposcan:** Fix vmaas_reader password setting ([`3ac9888`](https://github.com/RedHatInsights/vmaas/commit/3ac98880b8b97cb2d933f78918c370ee37095abf))

## v2.32.10 (2021-12-08)
### Performance
* **webapp:** Don't evaluate unfixed CVEs by default now ([`3bec6c8`](https://github.com/RedHatInsights/vmaas/commit/3bec6c8c936b41592c34751a61acb617399f4582))

## v2.32.9 (2021-12-07)
### Fix
* **webapp:** Allow CORS pre-flight check for /cves API ([`3a7c489`](https://github.com/RedHatInsights/vmaas/commit/3a7c489f5e8f72883522e1237d94611f7917bd1c))

## v2.32.8 (2021-11-25)
### Fix
* **websocket:** Do not advertise None vmaas cache version ([`a971fe0`](https://github.com/RedHatInsights/vmaas/commit/a971fe0559c1b55b0a531cbcc29d3c0a6d044cd4))

## v2.32.7 (2021-11-24)
### Fix
* **webapp:** Workaround with appProtocol tcp (clowder hardcodes http) - for istio ([`c5341d7`](https://github.com/RedHatInsights/vmaas/commit/c5341d7cbf3e65cac4abe21bfebd37ebeec61ffe))

## v2.32.6 (2021-11-19)
### Fix
* **reposcan:** Fetch actual data from db progressively ([`bbaf703`](https://github.com/RedHatInsights/vmaas/commit/bbaf7039ce048cd2b2c4aa13412ca4140c9a38c8))
* **reposcan:** Add template strings to properly update ([`60bf563`](https://github.com/RedHatInsights/vmaas/commit/60bf563b93379c9d54566121b05f427c6a2058e0))
* **reposcan:** Use cascade delete to properly delete ([`74b1c78`](https://github.com/RedHatInsights/vmaas/commit/74b1c784c24cb328cade9b7c260d429e3f273ccd))

## v2.32.5 (2021-11-15)
### Fix
* **reposcan:** Do not store 'None' string if last-modified header is not available ([`55e908a`](https://github.com/RedHatInsights/vmaas/commit/55e908a44734848c67f03d8e1c39f16c675027b8))

## v2.32.4 (2021-11-12)
### Fix
* **webapp:** Use common function for parsing evr ([`0724a04`](https://github.com/RedHatInsights/vmaas/commit/0724a04a8cb97cedef1ddeee26430816c43adbeb))

## v2.32.3 (2021-11-08)
### Fix
* **webapp:** Aiohttp 3.8.0 - don't create new event loop, fix websocket connection ([`2fb0494`](https://github.com/RedHatInsights/vmaas/commit/2fb0494d568fd4c17eb6be3995fee86b306eb3f9))

## v2.32.2 (2021-11-08)
### Fix
* **webapp:** Rebuild index array on cache reload ([`9062a6e`](https://github.com/RedHatInsights/vmaas/commit/9062a6e033026e227e2bc075ce99d2d2d5ddf88b))

## v2.32.1 (2021-11-08)
### Fix
* **webapp:** Remove empty release versions from list ([`77d7267`](https://github.com/RedHatInsights/vmaas/commit/77d72670271c71ddeaf3414c2b47eea7d430acfb))

## v2.32.0 (2021-11-02)
### Feature
* **webapp:** Update api spec with /pkglist endpoint ([`0b4aa64`](https://github.com/RedHatInsights/vmaas/commit/0b4aa645d2eb74022366fe7c325cde9b8cb02cd7))
* **webapp:** Add new /pkglist endpoint ([`a542839`](https://github.com/RedHatInsights/vmaas/commit/a542839164d4251bbc03355f99e7634e4ec29f82))
* **webapp:** Add "package_detail.modified" attribute and modified index to cache ([`50b1e4d`](https://github.com/RedHatInsights/vmaas/commit/50b1e4d642af0aa1add880de19e43be7f97ef863))
* Added common/algorithms.py module with find_index method ([`1431ee2`](https://github.com/RedHatInsights/vmaas/commit/1431ee24bad99a38531fd048d5b22df0e4cc70fa))

### Fix
* Upgrade db, use utc default timezon for "modified" pkg attribute ([`0c96b78`](https://github.com/RedHatInsights/vmaas/commit/0c96b7870b677dd63b3fe3030a47f8c4745867c7))

## v2.31.2 (2021-10-27)
### Fix
* **reposcan:** Skip populating empty repo data ([`b7a11b3`](https://github.com/RedHatInsights/vmaas/commit/b7a11b380dd4491d9b24eda4fb3c84af073c1ece))

## v2.31.1 (2021-10-27)
### Fix
* **reposcan:** Fixed implicit json serialization warning ([`7cb9ca0`](https://github.com/RedHatInsights/vmaas/commit/7cb9ca0c807da85b941c374f10a3f0c88fafb0a7))
* Updated lint related things ([`0ceacf8`](https://github.com/RedHatInsights/vmaas/commit/0ceacf839df8c687adb04c38e6b1dcd65a5c2290))
* Update deps ([`3afb539`](https://github.com/RedHatInsights/vmaas/commit/3afb53966ca4567ba76fc8dd2eff84909f006685))

## v2.31.0 (2021-10-21)
### Feature
* **webapp:** Exclude modified from cache for now ([`c4de51c`](https://github.com/RedHatInsights/vmaas/commit/c4de51cd07e844e4e9770940afc5b77f4551fd4d))
* **reposcan:** Updated package_store test, dump exporter and its tests ([`5debe20`](https://github.com/RedHatInsights/vmaas/commit/5debe20a723e7ed063b21e0a7cf36ac7a4b7e7a5))
* **reposcan:** SQL updates - added package.modified timestamp column ([`08d2b6a`](https://github.com/RedHatInsights/vmaas/commit/08d2b6a877afe2644383c5e6bae8cace179c97dd))

## v2.30.0 (2021-10-07)
### Feature
* **webapp:** Enhance /vulnerabilities API ([`613125d`](https://github.com/RedHatInsights/vmaas/commit/613125d640769bcb9f556a161c52ce0261bd4597))

## v2.29.0 (2021-10-07)
### Feature
* **webapp:** Enable optimistic updates for /vulnerabilities ([`d7c1fe0`](https://github.com/RedHatInsights/vmaas/commit/d7c1fe03ffff9089dd615e8b028b0ecab8eb309c))

## v2.28.4 (2021-10-07)
### Fix
* **webapp:** Load as many tables as possible even when dump is not up to date ([`751989b`](https://github.com/RedHatInsights/vmaas/commit/751989b6c9256575ac3071fae6bee93be9a4ae9b))

## v2.28.3 (2021-10-06)
### Fix
* **webapp:** Fix /pkgtree third-party repos info and third-party flag ([`717d79c`](https://github.com/RedHatInsights/vmaas/commit/717d79c820ed3e7f6b021b58b9cac7501b07225e))

## v2.28.2 (2021-10-05)
### Fix
* **webapp:** Fix /pkgtree endpoint when "modified_since" used ([`0f1d73e`](https://github.com/RedHatInsights/vmaas/commit/0f1d73ed3542b94a4cfa35156e941a338e7a7f6d))

## v2.28.1 (2021-09-17)
### Fix
* Set timeout for requests while waiting for services ([`ab4cb40`](https://github.com/RedHatInsights/vmaas/commit/ab4cb40b791df2e5f9558da664428574c1e9fad5))

## v2.28.0 (2021-09-14)
### Feature
* Delete stream requires when stream is deleted ([`db18b59`](https://github.com/RedHatInsights/vmaas/commit/db18b59c88057cd7ba9462a3b17e2d2ff2c1a1bf))
* Improve exporter test form module requires ([`dd79c7c`](https://github.com/RedHatInsights/vmaas/commit/dd79c7c3304167280fff939e67272f1df0784196))
* Updated test for module loading ([`e98fca9`](https://github.com/RedHatInsights/vmaas/commit/e98fca94b3307884f10dd7e3c7feee27c9d9433f))
* Fiter out module stream without satisfied requires ([`b0821bc`](https://github.com/RedHatInsights/vmaas/commit/b0821bc3982ded9111e1cb1d841703be0345fad9))
* Read module requires into cache ([`3b4afc7`](https://github.com/RedHatInsights/vmaas/commit/3b4afc72cb875a3200529f1cc288f3f5befa1e7e))
* Export module requires data ([`77b48c6`](https://github.com/RedHatInsights/vmaas/commit/77b48c61e4b8cb65a145a2d24e2db8c3d45fce47))
* Store module requires during reposcan ([`8487e65`](https://github.com/RedHatInsights/vmaas/commit/8487e65d70f8d0ed1357177d734aab2b7af52e37))
* Table to store module dependencies ([`24f3a25`](https://github.com/RedHatInsights/vmaas/commit/24f3a25a0f85edb8c5fc0164832302546e9711eb))

### Fix
* Silence pytest warnings ([`c71b03a`](https://github.com/RedHatInsights/vmaas/commit/c71b03ad08223bdff772dc895aeca3c70ed13431))
* Update developer setup to single app layout ([`9810bc2`](https://github.com/RedHatInsights/vmaas/commit/9810bc2ea42165ed9cd1c4005dbd45a344e95db2))

## v2.27.2 (2021-09-07)
### Fix
* **test:** Fixing new pylint warnings ([`024e118`](https://github.com/RedHatInsights/vmaas/commit/024e1186e7534ff7f38a22fda2ee64e11e8bec43))
* **test:** Fix pur deps to fix AttributeError: 'bool' object has no attribute 'lower' ([`1d73e3b`](https://github.com/RedHatInsights/vmaas/commit/1d73e3b92619afd15d7eb267cbcf869852c8cebe))

## v2.27.1 (2021-09-07)
### Fix
* **reposcan:** Fixed advisory "reboot_suggested" value parsing ([`85c1ddd`](https://github.com/RedHatInsights/vmaas/commit/85c1ddda23531c9118a7000d711cabae99c47eef))

## v2.27.0 (2021-09-06)
### Feature
* **webapp:** Added 'requires_reboot' to api docs (v3) ([`32440f2`](https://github.com/RedHatInsights/vmaas/commit/32440f2be2bc98fed7486e6dc1f0383923e2cb15))
* **webapp:** Added 'requires_reboot' to webapp ([`f222500`](https://github.com/RedHatInsights/vmaas/commit/f2225000eef4c7a632649ae87695de451d91f6eb))
* **reposcan:** Added 'requires_reboot' to dump exporter ([`309f35e`](https://github.com/RedHatInsights/vmaas/commit/309f35e2d3f6c097c432cac7429dbff4cf905dca))
* **reposcan:** Added option to disable some sync parts (git, cve, oval...) ([`f38da8e`](https://github.com/RedHatInsights/vmaas/commit/f38da8e14de4143bde3fd310f75166a79f8bc1aa))

## v2.26.1 (2021-09-06)
### Fix
* **webapp:** Fix /updates test for arch "(none)" ([`c24be27`](https://github.com/RedHatInsights/vmaas/commit/c24be272d61c2e385efbfd9da176c70ae58434bd))

## v2.26.0 (2021-09-03)
### Feature
* **reposcan:** Auto delete old oval items ([`38322bf`](https://github.com/RedHatInsights/vmaas/commit/38322bf6cd48585387d8e25d51f4bf5c7d669988))

## v2.25.0 (2021-09-01)
### Feature
* Implement requires_reboot flag for advisories ([`4a58f6d`](https://github.com/RedHatInsights/vmaas/commit/4a58f6d2d6c76b289d3b1e22aca2fcd0a377679e))
* **reposcan:** Automatically delete filtered/obsolete OVAL streams ([`bd977e2`](https://github.com/RedHatInsights/vmaas/commit/bd977e210c33a955ef23d0ab8bb7cf5e56533498))
* **reposcan:** Support deleting OVAL files ([`a499029`](https://github.com/RedHatInsights/vmaas/commit/a49902903fbe075f68aa16dbae3a8bb8c50a9b45))

### Fix
* **reposcan:** Disable rhel-7-alt OVAL stream ([`2ea9987`](https://github.com/RedHatInsights/vmaas/commit/2ea99875f6038b7fad13fc66e07a2aadf9f45e18))
* **database:** Add missing file_id foreign key ([`a6a23a9`](https://github.com/RedHatInsights/vmaas/commit/a6a23a95feb45a9560fd580ad84f095b6b1a6019))

## v2.24.1 (2021-07-28)
### Fix
* **clowder:** Use rds ca path ([`9f8a568`](https://github.com/RedHatInsights/vmaas/commit/9f8a5684d3dc02641d59926f31e1f4d975ecc274))

## v2.24.0 (2021-07-15)
### Feature
* **reposcan:** Support filtering OVAL files ([`29d555c`](https://github.com/RedHatInsights/vmaas/commit/29d555c7c67939e3e37eb3840935bc590b426450))

## v2.23.6 (2021-07-14)
### Fix
* **reposcan:** Fix slow re-syncs due to missing index ([`e9c9499`](https://github.com/RedHatInsights/vmaas/commit/e9c9499970d15a5c5e99be756982ad566724eff4))

## v2.23.5 (2021-07-12)
### Fix
* **reposcan:** Products being a list instead of dict in reposcan ([`cfba1fd`](https://github.com/RedHatInsights/vmaas/commit/cfba1fd69cd94af0a2c08aa458075f904e3b6bc3))

## v2.23.4 (2021-07-12)
### Fix
* Check=True throws subprocess.CalledProcessError in case of non-zero return code ([`cf4cee5`](https://github.com/RedHatInsights/vmaas/commit/cf4cee5e5bf164c9774e9c4ac64feb03b13b3284))

## v2.23.3 (2021-07-01)
### Fix
* **reposcan:** Remove parenthesis from returning statement ([`7e54a90`](https://github.com/RedHatInsights/vmaas/commit/7e54a904eeefc11473251ab1c3fc4f614019c8a3))

## v2.23.2 (2021-07-01)
### Fix
* **database:** Set ON_ERROR_STOP=on to have non-zero RC when error occurs, also don't rely on stderr ([`1046e97`](https://github.com/RedHatInsights/vmaas/commit/1046e976680670245eb40ce5f10ed946003b1de7))

## v2.23.1 (2021-07-01)
### Fix
* **database:** Apply migration file as single transaction ([`c64d11f`](https://github.com/RedHatInsights/vmaas/commit/c64d11f7b14411834657a29710ce1d0083976374))

## v2.23.0 (2021-07-01)
### Feature
* **database:** Bump database to rhel8/centos8 ([`8fc0b23`](https://github.com/RedHatInsights/vmaas/commit/8fc0b23953cb5a97f8accbca057e14f6dd223fd0))

## v2.22.1 (2021-07-01)
### Fix
* **reposcan:** Detect changes in oval files better ([`c69017a`](https://github.com/RedHatInsights/vmaas/commit/c69017a17f14a2ebdf7e3342bf1cab0d05eba906))
* **reposcan:** Sync OVAL data into updated schema ([`8a39630`](https://github.com/RedHatInsights/vmaas/commit/8a39630b6d6c5e5bc4e4da655157c4a3c7a91622))
* **database:** Re-structure OVAL-file associations ([`c3e2d6b`](https://github.com/RedHatInsights/vmaas/commit/c3e2d6b8374c5d91b91d1f616c840abc82fd9110))

## v2.22.0 (2021-06-17)
### Feature
* **reposcan:** Accept multiple repolists for git sync ([`f85f4a0`](https://github.com/RedHatInsights/vmaas/commit/f85f4a01b206063b1221de8853b5ce92aa6b30d0))

## v2.21.0 (2021-06-10)
### Feature
* **reposcan:** Retry periodic cache dump later if it failed ([`0694e3a`](https://github.com/RedHatInsights/vmaas/commit/0694e3a9f6c15164eeeedd4ce8b918704224681d))

## v2.20.2 (2021-06-09)
### Fix
* Bump app_common_python to get sslMode ([`b76eb7f`](https://github.com/RedHatInsights/vmaas/commit/b76eb7f8c70b245da94f5007825b034ec6d4daa5))
* Default ssl mode can't be empty string ([`17a366e`](https://github.com/RedHatInsights/vmaas/commit/17a366e40246c9a9106e06824a4abcccc6cff5f7))

## v2.20.1 (2021-06-08)
### Fix
* **webapp:** Revert: add "modified_since" to /v3/pkgtree response" ([`ae15ba0`](https://github.com/RedHatInsights/vmaas/commit/ae15ba02709fca396a6b678fdfdb84f4d0b35ade))

## v2.20.0 (2021-06-02)
### Feature
* Set PostgreSQL SSL mode ([`b5a555f`](https://github.com/RedHatInsights/vmaas/commit/b5a555f983e32dcb33be29a1a01f3f9b5e5cb32a))

## v2.19.2 (2021-05-25)
### Fix
* **webapp:** Add "modified_since" to /v3/pkgtree response ([`aee93a6`](https://github.com/RedHatInsights/vmaas/commit/aee93a6a20d1bee6a9f4af45d07e1ae6d399c79a))

## v2.19.1 (2021-05-25)
### Fix
* **webapp:** Comparison between srt and int, enhance split the string to int/str parts ([`315fee8`](https://github.com/RedHatInsights/vmaas/commit/315fee89628156b83956ddf71df928896d34ee89))
* **webapp:** If CVE is not in DB from cvemap, it's not connected with definition ([`d244df0`](https://github.com/RedHatInsights/vmaas/commit/d244df04e69c0b839f8674de9fc638890a0bb92c))

## v2.19.0 (2021-05-19)
### Feature
* **webapp:** Filter modules_list in OVAL evaluation ([`ab8011f`](https://github.com/RedHatInsights/vmaas/commit/ab8011f443a16299aab4f11aaa20f132bd32bb35))
* **reposcan:** Import OVAL module streams ([`0408efc`](https://github.com/RedHatInsights/vmaas/commit/0408efcec808297f09226c648eddb3f11f95279e))

## v2.18.1 (2021-05-17)
### Fix
* **reposcan:** Fix path to wait script and replace it with python version ([`8d40e09`](https://github.com/RedHatInsights/vmaas/commit/8d40e097d31632f0eb505b8de960ede448376117))

## v2.18.0 (2021-05-14)
### Feature
* **webapp:** Return HTTP 503 when no dump is loaded ([`5b7002a`](https://github.com/RedHatInsights/vmaas/commit/5b7002a968c1a12ca7a51c58b9fe1a3e7020468a))
* Add sqlite database format ([`eedcd53`](https://github.com/RedHatInsights/vmaas/commit/eedcd5330546a53f19894d621c3099b69ec0009c))

### Fix
* Third_party support, fix repo/errata/cve structure, updates order, datetime format etc. ([`e0e44a6`](https://github.com/RedHatInsights/vmaas/commit/e0e44a68c2d0b045a7f2aa203c8c36abdccaeea5))
* **webapp:** Load as set() and array.array('q') where previously ([`828a5f8`](https://github.com/RedHatInsights/vmaas/commit/828a5f89b9cd7b11ea0dc64f40440628fa753586))
* Export and load missing OVAL data ([`b02aa74`](https://github.com/RedHatInsights/vmaas/commit/b02aa74b80d0e87be8fb462100d9872ef1bb21ca))
* **reposcan:** Fix the package_name query ([`27aff01`](https://github.com/RedHatInsights/vmaas/commit/27aff01d12af26cf3d428bcba28d10c93d955e97))
* **webapp:** Productid2repoids was removed ([`3e461ee`](https://github.com/RedHatInsights/vmaas/commit/3e461eebd010825061ce2a53e10a6f243af52887))
* Move fetch_latest_dump out of DataDump ([`3b6eb9b`](https://github.com/RedHatInsights/vmaas/commit/3b6eb9bc0429187bcbd9f1c5e7fbc25db2e0ea39))
* **reposcan:** /data is mount point ([`a2c93b7`](https://github.com/RedHatInsights/vmaas/commit/a2c93b7f2fbd29bf313614b1ae45a4bd173a6400))

## v2.17.0 (2021-05-12)
### Feature
* **reposcan:** Allow repolists to opt_out of default certificates ([`dc00b21`](https://github.com/RedHatInsights/vmaas/commit/dc00b215c1b4d4283f87f9b63a02fa26fcc27aa1))

## v2.16.0 (2021-05-12)
### Feature
* **reposcan:** Accept lists for content set data ([`24be17e`](https://github.com/RedHatInsights/vmaas/commit/24be17ec2ae0ef344eca161556c617cefa95669b))

## v2.15.2 (2021-05-05)
### Fix
* **webapp:** Default to false until it's well tested, apps can request it anyway using param ([`646b3f6`](https://github.com/RedHatInsights/vmaas/commit/646b3f683a2e5eafd33a2750e0895aa8c4f153bd))

## v2.15.1 (2021-05-04)
### Fix
* **webapp:** Add more as_long_arr casts ([`17d5137`](https://github.com/RedHatInsights/vmaas/commit/17d513726b333445bcbfb012d1c6b0cd913cc100))
* **webapp:** Productid2repoids is not used ([`9483f9d`](https://github.com/RedHatInsights/vmaas/commit/9483f9dc18f113491b1371f472733f0a7c745691))

## v2.15.0 (2021-05-04)
### Feature
* **webapp:** Evaluate OVAL ([`06db2b1`](https://github.com/RedHatInsights/vmaas/commit/06db2b17148e10e3828a065401b57e3baf9800f9))
* **reposcan:** Export OVAL data ([`49b1ec4`](https://github.com/RedHatInsights/vmaas/commit/49b1ec461b8a37d82e2c4fc7edb3b0a714e48cf7))

### Fix
* **webapp:** Warn but don't crash ([`8f4c0c2`](https://github.com/RedHatInsights/vmaas/commit/8f4c0c294fd877a3e4ec26dac6b92f07db8a1079))

## v2.14.1 (2021-04-29)
### Fix
* **reposcan:** Fix KeyError when importing new repos ([`9303d34`](https://github.com/RedHatInsights/vmaas/commit/9303d347c364757e2af715321c53fb6415939c45))

## v2.14.0 (2021-04-28)
### Feature
* **reposcan:** Warn about extra repos in DB when syncing main repolist from git ([`5c5693d`](https://github.com/RedHatInsights/vmaas/commit/5c5693df8afc88d9bca0acb6924853ad754b78bc))

### Fix
* **reposcan:** Sync missing package names and EVRs ([`5079858`](https://github.com/RedHatInsights/vmaas/commit/507985819d9b6940debdf5b33080b32762743cbb))
* **reposcan:** Sync CPE substrings from OVAL files ([`605d020`](https://github.com/RedHatInsights/vmaas/commit/605d020a28a8bbaf67f043e24507d87e8739af11))

## v2.13.2 (2021-04-28)
### Fix
* **reposcan:** Optimize content deletion speed ([`b5fee66`](https://github.com/RedHatInsights/vmaas/commit/b5fee6630ec249bd89ee4b82da0edb875902edb6))
* **reposcan:** Delete from new dependent tables ([`ebcb5cb`](https://github.com/RedHatInsights/vmaas/commit/ebcb5cb83f58dd0342c9c12dc8ce745e5829c0f0))

## v2.13.1 (2021-04-21)
### Fix
* **webapp:** Include packages without errata ([`4b4e409`](https://github.com/RedHatInsights/vmaas/commit/4b4e409769dd14864f8275f51118beda159fa4d8))

## v2.13.0 (2021-04-20)
### Feature
* **webapp:** Add "modified_since" support to /pkgtree v3 ([`922c84b`](https://github.com/RedHatInsights/vmaas/commit/922c84bab2dc2af861f1d6cba362dc6dc58cc887))

## v2.12.0 (2021-04-20)
### Feature
* **webapp:** Add new /pkgtree endpoint options ([`5811f2f`](https://github.com/RedHatInsights/vmaas/commit/5811f2f6da52c8fbf192ce01944b230bb3a1d2bb))

## v2.11.0 (2021-04-19)
### Feature
* **webapp:** Added summary and description info to /pkgtree response v3 ([`909d7c3`](https://github.com/RedHatInsights/vmaas/commit/909d7c36368e003c616f21acff8df34204928929))

## v2.10.0 (2021-04-16)
### Feature
* **webapp:** Added pagination to /pkgtree (api_version=3) ([`568497d`](https://github.com/RedHatInsights/vmaas/commit/568497df7f29fa139c0544a863c525a613110ba4))

## v2.9.0 (2021-04-15)
### Feature
* **reposcan:** Add support for different git repolist branches ([`d7f8446`](https://github.com/RedHatInsights/vmaas/commit/d7f8446b35ad08ded908bd95d9e718ea1991b33a))

## v2.8.2 (2021-04-08)
### Fix
* **webapp:** Close dbm after loading cache ([`e6aad5c`](https://github.com/RedHatInsights/vmaas/commit/e6aad5c3f3e34527dd74ab347d5a272170d337b3))

## v2.8.1 (2021-04-08)
### Fix
* **reposcan:** Import CPEs even if not found in CPE dict ([`fba7ffb`](https://github.com/RedHatInsights/vmaas/commit/fba7ffb5e83ec89ce3d128cd5d40f3715e8df9da))
* **reposcan:** Empty insert ([`49022a4`](https://github.com/RedHatInsights/vmaas/commit/49022a415a964999b5ac45097f15c96d98be3990))

## v2.8.0 (2021-04-08)
### Feature
* **reposcan:** Support cleaning /tmp manually ([`504aa3d`](https://github.com/RedHatInsights/vmaas/commit/504aa3dd34839ee9b281b566c8f90ee711f80aef))

## v2.7.1 (2021-04-07)
### Fix
* **reposcan:** Handling of repolist urls ([`de3b8a0`](https://github.com/RedHatInsights/vmaas/commit/de3b8a0595bb5d0ff95d63258100ba47ab4a5445))

## v2.7.0 (2021-04-06)
### Feature
* **webapp:** Third party content support - Webapp ([`c001a8d`](https://github.com/RedHatInsights/vmaas/commit/c001a8db08efde47786ddcd119adf314288b5fea))

## v2.6.0 (2021-04-06)
### Feature
* **reposcan:** Parse and store OVAL data ([`c66d0e4`](https://github.com/RedHatInsights/vmaas/commit/c66d0e46931148a9dd57a14819b6d60f8d3be0b9))
* **reposcan:** Download OVAL files to tmp dir and unpack ([`737c0f3`](https://github.com/RedHatInsights/vmaas/commit/737c0f33baf748e2ee84561eeba5cadd26ec72b6))
* **reposcan:** Register sync API for OVAL files ([`9673f42`](https://github.com/RedHatInsights/vmaas/commit/9673f4224f06a1cd78a007f941a32cea113d4407))

## v2.5.0 (2021-03-29)
### Feature
* **reposcan:** Third-party content support, reposcan ([`7d203aa`](https://github.com/RedHatInsights/vmaas/commit/7d203aa6beb56a68d9e2338615472a89548e3e94))

## v2.4.1 (2021-03-26)
### Fix
* **webapp:** Fixed asserts in test_updates.py ([`f31e3dc`](https://github.com/RedHatInsights/vmaas/commit/f31e3dc3047a8a5d0edabbc4d32bdb9c1ad5332d))

## v2.4.0 (2021-03-23)
### Feature
* **webapp:** Define interface for patched/unpatched CVEs and OVAL evaluation toggles ([`125c839`](https://github.com/RedHatInsights/vmaas/commit/125c8397041c138b09c611d19095258151321aae))

## v2.3.0 (2021-03-18)
### Feature
* **webapp:** Show CPEs in /repos API ([`e080845`](https://github.com/RedHatInsights/vmaas/commit/e080845f5a3523f851dea20711fabd4a5f16ad0e))
* **reposcan:** Export imported CPE metadata ([`c1e441b`](https://github.com/RedHatInsights/vmaas/commit/c1e441bed7cc4e73c47fe203da7790d3c6545cc2))
* **reposcan:** Sync CPE metadata into DB ([`b688f9f`](https://github.com/RedHatInsights/vmaas/commit/b688f9f8eeee1d766a3b41c1e6c45978c6fd22f9))
* **database:** Introduce cpe tables ([`8247fde`](https://github.com/RedHatInsights/vmaas/commit/8247fded0468b7f19846b8d3827cdc13c1935bba))

## v2.2.1 (2021-03-08)
### Fix
* Waiting for DB and rsync port in e2e-deploy and docker-compose ([`9aad355`](https://github.com/RedHatInsights/vmaas/commit/9aad35511be74ef0dfa74ca5b8c8a829b08da3db))

## v2.2.0 (2021-03-05)
### Feature
* **clowder:** Integrate with clowder ([`e419895`](https://github.com/RedHatInsights/vmaas/commit/e419895249391f3a6c00f363435f97084ae2b215))

## v2.1.1 (2021-03-03)
### Fix
* **reposcan:** Replace github auth with turnpike ([`d0e5a4f`](https://github.com/RedHatInsights/vmaas/commit/d0e5a4f639fd00f9a9a5c12238ab1bb734526d87))

## v2.1.0 (2021-01-28)
### Feature
* **webapp:** Install rpm module ([`675c4e6`](https://github.com/RedHatInsights/vmaas/commit/675c4e67c1786f7074b33a1ab33f22c4032b3553))
* **webapp:** Update /updates to support latest_only filtering ([`e1fe2af`](https://github.com/RedHatInsights/vmaas/commit/e1fe2afa441f2d857410c318ae91bfebb938b953))
* **webapp:** Added function to filter latest NEVRAs ([`f1a662c`](https://github.com/RedHatInsights/vmaas/commit/f1a662ce2215006c1b09e0c07c2d28cc846b897a))
* Added cloudwatch logging setup ([`2bf4c2d`](https://github.com/RedHatInsights/vmaas/commit/2bf4c2def3a29cd5304bb8698508fa6bec813ff6))
* **reposcan:** Add cdn expiration notifications to slack ([`25e61f4`](https://github.com/RedHatInsights/vmaas/commit/25e61f400538b5f4ead453af74422ae82c658b51))
* **webapp:** Unify errata severity none to null ([`f2cddad`](https://github.com/RedHatInsights/vmaas/commit/f2cddad847ffdd6a9577a295945cb4f058cfc232))
* **webapp:** Return only those CVEs which have errata associated ([`c602508`](https://github.com/RedHatInsights/vmaas/commit/c602508179ec9083a86718d3c5e3379cbc1e05ff))
* **common:** Add slack notification module ([`3664752`](https://github.com/RedHatInsights/vmaas/commit/3664752de9429d7e2c9f0c0d2aaef8b830f06014))
* **webapp:** Add errata filtering by severity and errata type ([`b0b4df5`](https://github.com/RedHatInsights/vmaas/commit/b0b4df5308779551a9b3abd83e44e81b18972279))
* **webapp:** Add new POST and GET /package_names/rpms API endpoint ([`a64aa2e`](https://github.com/RedHatInsights/vmaas/commit/a64aa2e8b5b6fcb63a815387baec1724571cfa15))
* **webapp:** Add /package_names api endpoint ([`bda5cb5`](https://github.com/RedHatInsights/vmaas/commit/bda5cb5ef880b7a697c67ccf6d56870f2d64f9ca))
* **webapp:** New API to list only applicable errata to a package list ([`8c92679`](https://github.com/RedHatInsights/vmaas/commit/8c9267983ccc1f6a61a7575b4148be6f8a159dfe))
* **database:** Upgrade to PostgreSQL 12 ([`b6c61a9`](https://github.com/RedHatInsights/vmaas/commit/b6c61a9b25075135f0f7a461c5c3b8c3dee9b904))
* **database:** Add database upgrade scripts and tutorial ([`d5ce37e`](https://github.com/RedHatInsights/vmaas/commit/d5ce37e4b9ae8fd93adab80946ede0e36f5a5565))
* **reposcan:** Add function to check cert expiration date ([`857fe35`](https://github.com/RedHatInsights/vmaas/commit/857fe350fa95e1bfe10b9d946b3cde92bd8faee9))
* **webapp:** Add autoscaler to webapp, format secrets as a list of yaml values ([`58d7a56`](https://github.com/RedHatInsights/vmaas/commit/58d7a5697874d481163b59c120035b4e2add754b))
* **webapp:** Add lite error formatter ([`98bacd3`](https://github.com/RedHatInsights/vmaas/commit/98bacd3b0be1e76676bf6ad3a222e50dbf6902b1))
* **reposcan:** Add failed repo-download methrics for different http codes ([`80b71a8`](https://github.com/RedHatInsights/vmaas/commit/80b71a85b758df39e37d9ddaec611c89b67eb39a))
* Add pkgtree API endpoint to webapp ([#650](https://github.com/RedHatInsights/vmaas/issues/650)) ([`b56c681`](https://github.com/RedHatInsights/vmaas/commit/b56c681916919e85d690125e756c2a783a7195df))
* **reposcan:** Add metrics to count failed imports of cves and repos ([`e17de4d`](https://github.com/RedHatInsights/vmaas/commit/e17de4d5848195593d9b5c6eda7e1db7db978c67))
* **webapp:** Add new version of /updates API ([`3566ff2`](https://github.com/RedHatInsights/vmaas/commit/3566ff2088c875d55891c38fb8cfad654bd15d4b))
* **reposcan:** Export all updates, not only security ([`2373c48`](https://github.com/RedHatInsights/vmaas/commit/2373c484d956235d4341e736c9110a84c867ba89))
* **reposcan:** Don't sync CVEs from NIST ([`8d88702`](https://github.com/RedHatInsights/vmaas/commit/8d887020ca6fa00ffa52dfcf923633d4b043b860))
* **reposcan:** Add an api call to load repositories from git ([`92bf0ff`](https://github.com/RedHatInsights/vmaas/commit/92bf0ff056eae701edc56f408c35f80dc6925f68))

### Fix
* **webapp:** Check if websocket is open before message is sent and ensure concurrency ([`6f529d1`](https://github.com/RedHatInsights/vmaas/commit/6f529d1a014441c7341bd89f32bc32fde728685f))
* **reposcan:** Skip repos with invalid sqlite database ([`35388b5`](https://github.com/RedHatInsights/vmaas/commit/35388b551c3de19f745f50451601e898c3b09b7b))
* Duplicate messages in kibana ([`a296cb9`](https://github.com/RedHatInsights/vmaas/commit/a296cb97cc6b2c4ad344f323ddbc3835963a9b01))
* Use pod name for log-stream in CW config ([`f03fed4`](https://github.com/RedHatInsights/vmaas/commit/f03fed4ff38fa50a6c1f414618759b724f8e3fc2))
* **reposcan:** Detect case when sync process is killed and reposcan is stucked ([`b0797e8`](https://github.com/RedHatInsights/vmaas/commit/b0797e81b9d03cf54b647c02c4db188f7145006f))
* **webapp:** Init logging once ([`dcbaff3`](https://github.com/RedHatInsights/vmaas/commit/dcbaff349b57c9b711c3a0b73130c39708e5fde8))
* **webapp:** Only format error if response has body ([`07c60d0`](https://github.com/RedHatInsights/vmaas/commit/07c60d09a7aed0f7409ace5b486909346b71ec67))
* **webapp:** If there is no dump, websocket handler crashes due to KeyError ([`25ae1f5`](https://github.com/RedHatInsights/vmaas/commit/25ae1f55985ec32907c656ea5f6e9caf4518489f))
* **common:** Updated tests for rpm.parser_rpm_name ([`9c505bf`](https://github.com/RedHatInsights/vmaas/commit/9c505bf2fd4bb0c49e1a575fb1f359ebf5d614dc))
* Let pipenv see system site-packages ([`d5406ae`](https://github.com/RedHatInsights/vmaas/commit/d5406ae15def6b1194f3adca74563a2111dd14e3))
* Use new single app image ([`cb83321`](https://github.com/RedHatInsights/vmaas/commit/cb8332167b79f4accc87eed866b2a4ad74c4ad86))
* **reposcan:** Move function proper rpm module and reuse it ([`ba0124b`](https://github.com/RedHatInsights/vmaas/commit/ba0124b735bcd00446132694b4181792a24e0e7e))
* **webapp:** Reuse function from common.rpm ([`9c3b2fa`](https://github.com/RedHatInsights/vmaas/commit/9c3b2faae773a379b191dd523dbc08abcad8cdb2))
* **webapp:** Expose readiness endpoint ([`878d2c4`](https://github.com/RedHatInsights/vmaas/commit/878d2c4b3d3a07a74534dddafa806cd7bd054eb3))
* **webapp:** Don't block websocket during refresh ([`343044e`](https://github.com/RedHatInsights/vmaas/commit/343044ee957575ad62ad866a1e9ec59b3522813b))
* **websocket:** Track ids of clients in log ([`1b169fc`](https://github.com/RedHatInsights/vmaas/commit/1b169fcdbe8afc259cbc44cb6eecfe9f3366e0ed))
* **websocket:** Progressively refresh webapps ([`7f79ed4`](https://github.com/RedHatInsights/vmaas/commit/7f79ed4fb930a188e1403eda80d370c40d48bd24))
* Update developer mode to new single container ([`dd74dfa`](https://github.com/RedHatInsights/vmaas/commit/dd74dfab1e6b0f9a53661e4ccef05f07a1c6a90b))
* Build app image only once ([`a33dfdd`](https://github.com/RedHatInsights/vmaas/commit/a33dfddfde0da025cc4eb5d7427a13014e78e213))
* **reposcan:** File content is required by crypto lib, not file name, also fixing detection for certs expiring in more than 30 days ([`11917f3`](https://github.com/RedHatInsights/vmaas/commit/11917f31e620f911f07be3745f882b716c93bca2))
* **reposcan:** Fixing ISE in prepare msg function ([`04c7258`](https://github.com/RedHatInsights/vmaas/commit/04c7258dfc630172ace90e73ad7ee8cfbe9c0104))
* Fix path to wait script ([`d0fcdc1`](https://github.com/RedHatInsights/vmaas/commit/d0fcdc103970cdcdda68e781bc902fa4541209ce))
* **reposcan:** Export pkg_cve mappings only for cves with source ([`3bb9bac`](https://github.com/RedHatInsights/vmaas/commit/3bb9bacc56b6502f6f11aa5e88f1bba11ed5f564))
* **websocket:** Fix key error and incorrect timestamp extraction ([`3c0e4c0`](https://github.com/RedHatInsights/vmaas/commit/3c0e4c0815deaff3fa0c359fd88878dab54b56f7))
* **webapp:** Added non module testing update into the webapp tests ([`3041854`](https://github.com/RedHatInsights/vmaas/commit/30418541e9f403a6d5028534cf8a35ac2b28f95b))
* **webapp:** Updated tests default modules update ([`ad063ef`](https://github.com/RedHatInsights/vmaas/commit/ad063ef46647596ef6e9936ea9d8e28cc356e3cd))
* **webapp:** Removed updates when modules_list is not provided ([`952a89c`](https://github.com/RedHatInsights/vmaas/commit/952a89cdaa5a907cd753bbe009aefa26fe64b22e))
* **webapp:** Fixed webapp response gzipping ([`29d7988`](https://github.com/RedHatInsights/vmaas/commit/29d798845dc0bfcdb1898cdd6dc4d43f85b13644))
* **reposcan:** Delete rows from module_rpm_artifact ([`f8889a4`](https://github.com/RedHatInsights/vmaas/commit/f8889a4fc3449bdc29187518e0d500f83948f8c0))
* **reposcan:** Add src_pkg_names to content set mapping to cache ([`c7020e7`](https://github.com/RedHatInsights/vmaas/commit/c7020e701616a2adcef033bc5a5cb6f1b39803de))
* **reposcan:** Fix bugs in db tests ([`4156bfb`](https://github.com/RedHatInsights/vmaas/commit/4156bfbcceea1b12d7756aa76413e3556905c0ed))
* **reposcan:** Close DB connection when background tasks finishes ([`4d0d3a8`](https://github.com/RedHatInsights/vmaas/commit/4d0d3a84903f5eb91119443cfe066249b7a20a19))
* **webapp:** Removed redundant product check ([`1a8a5ba`](https://github.com/RedHatInsights/vmaas/commit/1a8a5ba355ab314143653a7d8e8eb421c3de7a59))
* **webapp:** Fixed gzip middleware null-pointer ([`134fcf8`](https://github.com/RedHatInsights/vmaas/commit/134fcf8da5ed598701416ceb59b6ebd5f41ad5d8))
* **reposcan:** Export package names without errata ([`05fe569`](https://github.com/RedHatInsights/vmaas/commit/05fe569a6377a6a0defbc17f81f45217b85cefb0))
* **webapp:** Fix content set filtering in package_names/srpms api endpoint ([`ee323bf`](https://github.com/RedHatInsights/vmaas/commit/ee323bfc0da8ad80efffe8c936d80f488f862214))
* **webapp:** Remove unused argument and imports ([`5a695d7`](https://github.com/RedHatInsights/vmaas/commit/5a695d72561f1899c1538caae50efc2246bfd6eb))
* **webapp:** Removed hotcache ([`68e7528`](https://github.com/RedHatInsights/vmaas/commit/68e75287205d5107a6393d7995e56f872ad40dbc))
* **webapp:** Distinguish existining and nonex. packages on /rpms ([`e417401`](https://github.com/RedHatInsights/vmaas/commit/e4174019434d0b00a2d6c8be30c80771ae8c2036))
* **webapp:** Distinguish existining and nonex. packages on /srpms ([`d7f4e50`](https://github.com/RedHatInsights/vmaas/commit/d7f4e500a320cc6916c196ed4bd9b88097b82f40))
* **reposcan:** Do not show bad token to log ([`c4f1c0d`](https://github.com/RedHatInsights/vmaas/commit/c4f1c0d36556860ffd40250f18a1f3cc7db1208a))
* Patches API should return ALL errata, not just security ones ([`82f80a8`](https://github.com/RedHatInsights/vmaas/commit/82f80a87c136791643ef6285e900bc2455bb3fc4))
* There may not be any dump loaded ([`4fbb326`](https://github.com/RedHatInsights/vmaas/commit/4fbb3268f7ccc5077281b093dd5303e7c983fde0))
* **database:** Default 64mb is not always enough for PostgreSQL 12 ([`0677cab`](https://github.com/RedHatInsights/vmaas/commit/0677cab792eec7e4928251055f96ebcf04616ee4))
* **webapp:** Switch to refreshing mode and return 503 ([`f5e15ab`](https://github.com/RedHatInsights/vmaas/commit/f5e15ab4a52f81d1b4d4ef3510c7d7773d7f1516))
* **webapp:** Don't block API during cache refreshes ([`9b85909`](https://github.com/RedHatInsights/vmaas/commit/9b8590991853d94f4b40e75967624f6a861ced01))
* **reposcan:** 8.1-409 has broken dependencies in UBI repo ([`edfee79`](https://github.com/RedHatInsights/vmaas/commit/edfee7945f61d40565ea1dcf9504c38f4e3508bd))
* **webapp:** Fix cache data race fetching when websocket crashes ([`d9c9ae8`](https://github.com/RedHatInsights/vmaas/commit/d9c9ae8acee1ada883e3cb4e7dc0cc3c5a1d28e5))
* **webapp:** Add webapp automatical reconnect to ws ([`403e209`](https://github.com/RedHatInsights/vmaas/commit/403e209ff5a9d7dcd7d58ce1a005c1dab2a9d902))
* **reposcan:** PG 12 to_timestamp() behaviour changed ([`1a05925`](https://github.com/RedHatInsights/vmaas/commit/1a05925f032c48323f0be3b5b2a1e82838b89350))
* 'pipenv install' re-generates lockfile by default, install only from what's already in lockfile ([`3fde6d4`](https://github.com/RedHatInsights/vmaas/commit/3fde6d4fc8a1a4008f9bb4914f007cbfdc0cc772))
* Update pyyaml (CVE-2020-1747) and some others to fix tests ([`24a6890`](https://github.com/RedHatInsights/vmaas/commit/24a68904f23ada927bc1687aff11630bc664d5e9))
* **reposcan:** Duplicate error when import repos ([`29d275e`](https://github.com/RedHatInsights/vmaas/commit/29d275e96b6cc684c048112dfa7e8bff86c4efd7))
* **reposcan:** Install postgresql for DB migrations ([`e8b6210`](https://github.com/RedHatInsights/vmaas/commit/e8b621092b5ffd2e282ebc44c25c29e4fc6fbf19))
* **reposcan:** Set source id to null instead of deleting it ([`613c615`](https://github.com/RedHatInsights/vmaas/commit/613c6150fdb0ecff2dc535f74ffa718728ac4624))
* **reposcan:** Invalidate webapp cache only when task succeeded ([#678](https://github.com/RedHatInsights/vmaas/issues/678)) ([`c9befc5`](https://github.com/RedHatInsights/vmaas/commit/c9befc5cc97bbebc9fddddab116f096e4e1775d4))
* Check on system level to find vulnerabilities and workaround pipenv to make it work ([`6c5f6db`](https://github.com/RedHatInsights/vmaas/commit/6c5f6dbab5e21c20ea1bbac6d61c587f0776f1b2))
* Revert "temporarily ignore cve in pipenv" ([`20e535b`](https://github.com/RedHatInsights/vmaas/commit/20e535b37f7f3c4161b941952b372274b2da0fea))
* Temporarily ignore cve in pipenv ([`ec23cb5`](https://github.com/RedHatInsights/vmaas/commit/ec23cb5226ded5d245c3bfce244f190481ad676c))
* **reposcan:** Use left join instead of inner ([`1288da4`](https://github.com/RedHatInsights/vmaas/commit/1288da4d29f2de511353786021085e21db810037))
* **webapp:** Set 415 error code and change detail message for incorrect content type ([`bd37916`](https://github.com/RedHatInsights/vmaas/commit/bd37916779c55555d63d21c7f47d6d5457a664e5))
* **database:** Store null severity in errata table ([`0657527`](https://github.com/RedHatInsights/vmaas/commit/065752791726a28f7f934b3b409ca2a03e6009fa))
* **reposcan:** Repo is empty string because stdout of git clone is empty ([`91a7e75`](https://github.com/RedHatInsights/vmaas/commit/91a7e75ab6b297282ca9dc0cbfa9b44cd420bdca))
* **reposcan:** Init logging in Git sync ([`c10fff8`](https://github.com/RedHatInsights/vmaas/commit/c10fff83c7f03c8c0d1fbc976d7d95327d6a8b3d))
* **manifests:** Fix manifest push process ([`c48d226`](https://github.com/RedHatInsights/vmaas/commit/c48d2268f868760d4be24e6b96d76e130f7a1036))
* Obsolete Dockerfile diff test ([`9167f22`](https://github.com/RedHatInsights/vmaas/commit/9167f228ac30b6e2a80df1a3df10ba5582204acb))
* Obsolete suffixes in OpenShift deployment ([`a9f21fd`](https://github.com/RedHatInsights/vmaas/commit/a9f21fdb69bcd8064f01a05ab951c065420e2523))
* **reposcan:** Xml tree evaluates found elements as False ([`8e7b24e`](https://github.com/RedHatInsights/vmaas/commit/8e7b24edfe3ef172cce709e744c2d067f1ef538b))
* **reposcan:** Duplicate conflict while importing repos ([`ffd4b00`](https://github.com/RedHatInsights/vmaas/commit/ffd4b00a9e81a79e3b432bc3ee1008df3d9dfd16))
* **reposcan:** Syntax error while deleting repos ([`a58e48c`](https://github.com/RedHatInsights/vmaas/commit/a58e48c185b0378d67d5ce4993c593444da88c4a))
* **reposcan:** Delete module by repo fk reference ([`d192ff1`](https://github.com/RedHatInsights/vmaas/commit/d192ff1b4667c8cbc60f7f59c6e4cae07c8e2ede))
* **webapp:** Fix 500 error when empty modules_list ([`caa6edf`](https://github.com/RedHatInsights/vmaas/commit/caa6edf198ae5b87af1b8b89519c6113c17d8b08))
* **reposcan:** Optimize and fix source package associations ([`9d41a50`](https://github.com/RedHatInsights/vmaas/commit/9d41a50163916e2e19330a0ff00f3d9f1983257c))
* **reposcan:** Store references from cvemap as secondary url ([`8934aac`](https://github.com/RedHatInsights/vmaas/commit/8934aac47431d16507fd96f1d25cadf59999cb8e))
* **reposcan:** Create always pre-defined redhat_url ([`fd2efe8`](https://github.com/RedHatInsights/vmaas/commit/fd2efe8301a1f562097028b3906843317b6d8968))
* **reposcan:** Sync IAVA when available ([`1768ad7`](https://github.com/RedHatInsights/vmaas/commit/1768ad7b8e66a00cff0783961fe42bea4cbbd7ab))
* **reposcan:** Pkgtree is exported and not synced, fix endpoints ([`f762c46`](https://github.com/RedHatInsights/vmaas/commit/f762c46d0efea3b4795d3342bd03477ade2454b1))
* **webapp:** Fix sending message to websocket ([`aa54f0b`](https://github.com/RedHatInsights/vmaas/commit/aa54f0b35f4cb62a26b94d62403c00efc88ecc3e))
* **reposcan:** Revision has to be updated but only sometimes ([`66a4e43`](https://github.com/RedHatInsights/vmaas/commit/66a4e4394b621149473ea905325de464b281d977))
* Correctly display version in swagger ([`c88f0d1`](https://github.com/RedHatInsights/vmaas/commit/c88f0d14621b8d1f1b1c05494bb970bcbfba3211))
* **reposcan:** Don't reset timestamp and update only things that make sense ([`153371b`](https://github.com/RedHatInsights/vmaas/commit/153371b084db186b84959cdee0ebc1565c705e17))
* **reposcan:** Add missing default CDN cert variables ([`4cdd962`](https://github.com/RedHatInsights/vmaas/commit/4cdd962094fbae813d22b1e6682709012660c87f))
* **reposcan:** Don't flood logs with error when there is lot of errors ([`62fb346`](https://github.com/RedHatInsights/vmaas/commit/62fb34655e027e0faad88bfc248240f6a22646ec))
* **reposcan:** Run git download in periodic sync ([`4d732da`](https://github.com/RedHatInsights/vmaas/commit/4d732da49bd5afc5b84afe8dc23d3036e3f44235))
* **reposcan:** Change endpoint to more appropriate ([`cfb7672`](https://github.com/RedHatInsights/vmaas/commit/cfb7672cd114b4d76f6a6c420cab118e1965d66f))
* **reposcan:** Don't run export when new (empty) repos are added ([`75d027a`](https://github.com/RedHatInsights/vmaas/commit/75d027acf8e345a50dada03ed9b709f8085d65cf))
* **reposcan:** Fix github access from openshift ([`7949e82`](https://github.com/RedHatInsights/vmaas/commit/7949e82ffae71dc5a12c7f8c6da29559236072c9))

### Documentation
* Specify possible values in schema ([`75a6de7`](https://github.com/RedHatInsights/vmaas/commit/75a6de7575b37f345ab2517343535ee56cf33060))

## v1.20.7 (2021-01-05)
### Fix
* **webapp:** Check if websocket is open before message is sent and ensure concurrency ([`6f529d1`](https://github.com/RedHatInsights/vmaas/commit/6f529d1a014441c7341bd89f32bc32fde728685f))

## v1.20.6 (2020-12-03)
### Fix
* Skip repos with invalid sqlite database ([`35388b5`](https://github.com/RedHatInsights/vmaas/commit/35388b551c3de19f745f50451601e898c3b09b7b))

## v1.20.5 (2020-11-19)
### Fix
* Duplicate messages in kibana ([`a296cb9`](https://github.com/RedHatInsights/vmaas/commit/a296cb97cc6b2c4ad344f323ddbc3835963a9b01))

## v1.20.4 (2020-10-29)
### Fix
* Use pod name for log-stream in CW config ([`f03fed4`](https://github.com/RedHatInsights/vmaas/commit/f03fed4ff38fa50a6c1f414618759b724f8e3fc2))

## v1.20.3 (2020-10-09)
### Fix
* Detect case when sync process is killed and reposcan is stucked ([`b0797e8`](https://github.com/RedHatInsights/vmaas/commit/b0797e81b9d03cf54b647c02c4db188f7145006f))
