# Changelog

<!--next-version-placeholder-->

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
