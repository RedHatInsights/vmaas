# CHANGELOG

## v2.62.4 (2024-07-25)

### Fix

* fix: add internal endpoint for profiling webapp-go

RHINENG-11507 ([`451d8c2`](https://github.com/RedHatInsights/vmaas/commit/451d8c2971967458dfec1a91c7b535a298bf8a7b))

## v2.62.3 (2024-07-23)

### Fix

* fix: update dependencies

RHINENG-11425 ([`b143604`](https://github.com/RedHatInsights/vmaas/commit/b143604914fdb1ba8264fe0795eb7017e1591c41))

## v2.62.2 (2024-07-23)

### Fix

* fix: stop using beta vex files

RHINENG-11599 ([`3c34f7b`](https://github.com/RedHatInsights/vmaas/commit/3c34f7bf103c9bea8c966ddb6a43a87328a0f667))

## v2.62.1 (2024-07-04)

### Fix

* fix: detect all affected packages for unfixed vulns

RHINENG-11201 ([`052b781`](https://github.com/RedHatInsights/vmaas/commit/052b781c4e8390c869ad9bf2f348fdb20b6b7549))

## v2.62.0 (2024-07-02)

### Feature

* feat(webapp-go): report module info for unfixed CVEs

RHINENG-10771 ([`ec1ca01`](https://github.com/RedHatInsights/vmaas/commit/ec1ca013b54ab551ef162f97b68499ccadc73a32))

## v2.61.9 (2024-06-27)

### Chore

* chore: new pylint ([`4048e0c`](https://github.com/RedHatInsights/vmaas/commit/4048e0c4d42ea0203880df81c1a2acd6883b7c21))

* chore: update dependencies

RHINENG-10319 ([`fda9928`](https://github.com/RedHatInsights/vmaas/commit/fda9928a102f4f944917520bf2631fb9d6d4483d))

* chore: increase webapp memory request/limit ([`364f681`](https://github.com/RedHatInsights/vmaas/commit/364f681b374b068e59a772f7335ae347d3764e8a))

### Fix

* fix: match cpe pattern substrings

RHINENG-10943 ([`e3b5f54`](https://github.com/RedHatInsights/vmaas/commit/e3b5f54e6cab5b69950a7cb8d3cbbebd9f8301c9))

## v2.61.8 (2024-06-20)

### Fix

* fix(csaf): increase default memory request for webapp-go ([`a126792`](https://github.com/RedHatInsights/vmaas/commit/a12679247fe67a785a1df6b968388e49444f5b2f))

* fix(csaf): use purl,parse only rpm products

RHINENG-9590 ([`1623068`](https://github.com/RedHatInsights/vmaas/commit/162306825f829b622e65c20b0ea067dbb5de1c51))

## v2.61.7 (2024-06-20)

### Fix

* fix: string formatting in CloudWatch

RHINENG-8336 ([`7d2d84d`](https://github.com/RedHatInsights/vmaas/commit/7d2d84d61e592bee4e79fcc371d9c1e1eca011fa))

### Unknown

* RHINENG-10310: manually_fixable_cves from csaf ([`b8a9908`](https://github.com/RedHatInsights/vmaas/commit/b8a990818f69b9d5d5af358d1265b2f44036b5c7))

## v2.61.6 (2024-06-18)

### Fix

* fix(csaf): download only files from csv

RHINENG-10605 ([`423c7a5`](https://github.com/RedHatInsights/vmaas/commit/423c7a5fe2bcbc8e1179e57e2f5ec4bdf5266609))

## v2.61.5 (2024-06-18)

### Fix

* fix(reposcan): exclude under investigation CVEs from OVAL

RHINENG-9878 ([`0aa518a`](https://github.com/RedHatInsights/vmaas/commit/0aa518a72210b7da1126a1cf5e6f20970785cb19))

### Unknown

* Adding Security-Scan Script to Enable Jenkins Security Scan Job ([`5a56460`](https://github.com/RedHatInsights/vmaas/commit/5a564604bb1006f783bcd617ec5bb88597f321ff))

## v2.61.4 (2024-06-13)

### Chore

* chore(reposcan): add OVAL_SYNC_ALL_FILES flag ([`484a105`](https://github.com/RedHatInsights/vmaas/commit/484a105d03007ade05d28ff03062e4eabbd9161a))

### Fix

* fix(csaf): syntax error with IN query

vmaas-reposcan          | vmaas-reposcan 2024-06-03 17:50:17,781:ERROR:vmaas.reposcan.database.object_store:Failed to import csaf file to DB: &#39;Traceback (most recent call last):\n  File &#34;/vmaas/vmaas/reposcan/database/csaf_store.py&#34;, line 75, in _save_csaf_files\n    cur.execute(&#34;select id, name from csaf_file where name in %s&#34;, (tuple(files),))\npsycopg2.errors.SyntaxError: syntax error at or near &#34;)&#34;\nLINE 1: select id, name from csaf_file where name in ()\n                                                      ^\n&#39;|

RHINENG-10604 ([`37b1e31`](https://github.com/RedHatInsights/vmaas/commit/37b1e31b7ba8de8e0c417065aeb28f958773a2a9))

## v2.61.3 (2024-06-07)

### Fix

* fix(build): update it-root-ca

RHINENG-10539 ([`c1d7cca`](https://github.com/RedHatInsights/vmaas/commit/c1d7ccad297831e22c6944fa1789f72b90e31d1c))

## v2.61.2 (2024-06-06)

### Fix

* fix: store package_name_id for fixed csaf_product

RHINENG-10310 ([`bd09fe2`](https://github.com/RedHatInsights/vmaas/commit/bd09fe25b019f2f75f6efb5e161cf09ea2ec11b1))

## v2.61.1 (2024-06-06)

### Chore

* chore: waive CVE-2019-8341 jinja2 (old CVE, we&#39;re using latest version, false positive?) ([`d66c1f2`](https://github.com/RedHatInsights/vmaas/commit/d66c1f25ba4e2a846ad0b89fffcfe69aba669cc3))

* chore: Centos 8 Stream was removed, install postgresql and rpm-devel from COPR ([`dd006c6`](https://github.com/RedHatInsights/vmaas/commit/dd006c668178412d76d90c8532be56ebd4060831))

### Fix

* fix: include levelname in CW logs from python code

RHINENG-8336 ([`eca466c`](https://github.com/RedHatInsights/vmaas/commit/eca466c4c6acfb6ac5bc4fa846499f3dc06a89b7))

## v2.61.0 (2024-05-31)

### Chore

* chore(csaf): log warning if there are multiple errata

RHINENG-10310 ([`7df7880`](https://github.com/RedHatInsights/vmaas/commit/7df7880517a0aa320546312b917cc58aeca5467e))

* chore(csaf): raise NotImplementedError for unsupported status_id

RHINENG-10310 ([`555b28d`](https://github.com/RedHatInsights/vmaas/commit/555b28d0526ced6221d2f87ab89caf29f8d68ddc))

* chore: update go version and dependencies

RHINENG-9601 ([`42162e2`](https://github.com/RedHatInsights/vmaas/commit/42162e20c20e844f31897380e4ef8e227a9753ba))

### Feature

* feat(csaf): dump erratum

RHINENG-10310 ([`90443d3`](https://github.com/RedHatInsights/vmaas/commit/90443d357d4e082ac94393019c896dae4ff211bf))

* feat(csaf): save errata to db

RHINENG-10310 ([`5450b60`](https://github.com/RedHatInsights/vmaas/commit/5450b6041913977fcf3f62da4fe2d70daab5e610))

* feat(csaf): add errata to db schema

RHINENG-10310 ([`f6a5a12`](https://github.com/RedHatInsights/vmaas/commit/f6a5a126127621ead0a4b538cf76f5118c65e2e3))

* feat(csaf): parse fixed csaf vex products

RHINENG-10310 ([`6f2580d`](https://github.com/RedHatInsights/vmaas/commit/6f2580d5e6c348d5a6b84296b7e7b94b68628d23))

### Fix

* fix(csaf): start processing fixed product status

RHINENG-10310 ([`c0a97e9`](https://github.com/RedHatInsights/vmaas/commit/c0a97e92dd6d42cb3fcb4951b30eb848d3cb3c75))

### Test

* test(csaf): extend test with errata parsing

RHINENG-10310 ([`572cc41`](https://github.com/RedHatInsights/vmaas/commit/572cc414b683599d38e83af1432a6a4770f634e2))

## v2.60.4 (2024-05-28)

### Fix

* fix(csaf): cves for source packages

RHINENG-9890 ([`6b7c3dc`](https://github.com/RedHatInsights/vmaas/commit/6b7c3dc7005fadfe06355cd21a6308388bb848b5))

## v2.60.3 (2024-05-16)

### Fix

* fix(csaf): remove products if they become fixed/unaffected

RHINENG-10039 ([`f6b4702`](https://github.com/RedHatInsights/vmaas/commit/f6b470263b6d4af7e30cbc37897a58f7065d6621))

## v2.60.2 (2024-05-16)

### Chore

* chore(csaf_test): fix input for test_csaf_store

use correct CsafData content to call `store` function, this commit is not fixing the test itself which does not seem to have any asserts, test just runs the code ([`99d29c2`](https://github.com/RedHatInsights/vmaas/commit/99d29c27075bf19dd401c48e3b4fd0b910f9821f))

* chore: update dependencies

RHINENG-10048 ([`79be3aa`](https://github.com/RedHatInsights/vmaas/commit/79be3aa7f551c8e9cfb07250b4ca6bc8d41dd3f6))

### Fix

* fix(csaf): update file timestamp for skipped cve

RHINENG-9586 ([`ca43ccc`](https://github.com/RedHatInsights/vmaas/commit/ca43ccc581b707a6889caf48eaa62ff94201478f))

## v2.60.1 (2024-04-30)

### Fix

* fix: update vmaas-lib to improve concurrency

RHINENG-9798
RHINENG-9797 ([`112d19c`](https://github.com/RedHatInsights/vmaas/commit/112d19cede5b26978e1e25e9fad0b254f1f6b351))

## v2.60.0 (2024-04-29)

### Feature

* feat(csaf): use csaf in /vulnerabilities

RHINENG-7869 ([`7eb8980`](https://github.com/RedHatInsights/vmaas/commit/7eb8980b6d8866c86dc0cd268f3f42d5da1a5527))

## v2.59.0 (2024-04-25)

### Feature

* feat: list modified packages in modified repos

RHINENG-9690 ([`d9a8181`](https://github.com/RedHatInsights/vmaas/commit/d9a818179e0417ce202d5b4ff21f3853a65fa22a))

## v2.58.4 (2024-04-25)

### Chore

* chore(deps): bump golang.org/x/net from 0.18.0 to 0.23.0 in /vmaas-go

Bumps [golang.org/x/net](https://github.com/golang/net) from 0.18.0 to 0.23.0.
- [Commits](https://github.com/golang/net/compare/v0.18.0...v0.23.0)

---
updated-dependencies:
- dependency-name: golang.org/x/net
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`c7e6423`](https://github.com/RedHatInsights/vmaas/commit/c7e64233ae9d38fcd12d2850ab205ec5d5ee6547))

* chore: upgrade to latest idna

RHINENG-9574 ([`3230ca4`](https://github.com/RedHatInsights/vmaas/commit/3230ca4006a71ab85d7d4fe1d3454628af6b0c94))

### Fix

* fix(build_deploy): only create sc tag when building sc branch ([`6b2e818`](https://github.com/RedHatInsights/vmaas/commit/6b2e81844cc4f311daf4eac9306c75007abb8ffb))

## v2.58.3 (2024-04-17)

### Fix

* fix(csaf): query argument

RHINENG-9510 ([`61cae18`](https://github.com/RedHatInsights/vmaas/commit/61cae1881db429a94043db56935190a448b74e1c))

## v2.58.2 (2024-04-17)

### Fix

* fix(csaf): populate mapping with updated files

RHINENG-9510 ([`81b4ce6`](https://github.com/RedHatInsights/vmaas/commit/81b4ce627553d1084aa1b4356249de9aa158d9f4))

## v2.58.1 (2024-04-17)

### Fix

* fix(reposcan): add internal /download/pg_dump api

RHINENG-9441 ([`92f1f31`](https://github.com/RedHatInsights/vmaas/commit/92f1f3184e292029580ee5eb48476ebfc832442c))

## v2.58.0 (2024-04-11)

### Feature

* feat(csaf): load csaf dump in webapp

RHINENG-9212 ([`770d7ed`](https://github.com/RedHatInsights/vmaas/commit/770d7ed5e78056f062ce4a4e9bc039adc59d9e36))

## v2.57.1 (2024-04-11)

### Chore

* chore(csaf): fix count of files in log ([`6807625`](https://github.com/RedHatInsights/vmaas/commit/68076251a9e84a7160058216bc388320ca47b839))

### Fix

* fix(csaf): improve module parsing from csaf

RHINENG-7868 ([`17e41dc`](https://github.com/RedHatInsights/vmaas/commit/17e41dc31acedc69675ddba522b5ed9534b39316))

## v2.57.0 (2024-04-04)

### Chore

* chore: update cryptography package ([`c986484`](https://github.com/RedHatInsights/vmaas/commit/c9864849e8b59ac021b677fea8a9baf506faf275))

### Feature

* feat(reposcan): Add CSAF SQLite dump ([`11c8897`](https://github.com/RedHatInsights/vmaas/commit/11c88979f63282bfdc76b88958ce40246ffd6e93))

## v2.56.1 (2024-03-25)

### Chore

* chore: update protobuf ([`b3837dd`](https://github.com/RedHatInsights/vmaas/commit/b3837ddd7e2f34e536986f60efb8822bcd8ba4c4))

* chore(tests): capture logs in tests ([`d88e119`](https://github.com/RedHatInsights/vmaas/commit/d88e119b76e406dd6af4a744ddc021ce2a8c0fb6))

* chore(csaf): add csaf_store tests ([`edc0943`](https://github.com/RedHatInsights/vmaas/commit/edc0943d72b256c588561d4b00db35a7091f7764))

* chore(csaf): extend model tests ([`9218f7a`](https://github.com/RedHatInsights/vmaas/commit/9218f7a8f5f8bffce1d9cb264c69766330c1a309))

* chore(mypy): improve checks and fix issues found by mypy ([`404e2ea`](https://github.com/RedHatInsights/vmaas/commit/404e2ea5ef57d7a9bc7578ab48ce1655c68d3c14))

* chore(csaf): make sure CVEs are always uppercase ([`272b57d`](https://github.com/RedHatInsights/vmaas/commit/272b57d2894984285ccc6407b2cf51a029c9e131))

* chore(csaf): move csaf test data to conftest ([`a818921`](https://github.com/RedHatInsights/vmaas/commit/a81892191b31d19e21020870232c7bf224041e61))

* chore: ignore CVE-2023-6129 as we&#39;re not affected

not running on PPC
using the lib only for checking expiration dates ([`45fdf5e`](https://github.com/RedHatInsights/vmaas/commit/45fdf5e0156283cc5f22632295ae09bf19ba471b))

### Fix

* fix(csaf): store unique products to collection ([`31e1e4a`](https://github.com/RedHatInsights/vmaas/commit/31e1e4a8cba3841a7fcd9a6a197b2ba54af4e2eb))

* fix(csaf): insert missing cpes ([`0942fd0`](https://github.com/RedHatInsights/vmaas/commit/0942fd01eebe6beda5c7e14a49fe547e812ecede))

* fix(csaf): update file timestamp after successful cve insert/remove ([`2565635`](https://github.com/RedHatInsights/vmaas/commit/25656356bdb5b0ed2ff6e9b4d236f70191b4cd6e))

* fix(csaf): don&#39;t guess cve name by file name ([`6759e29`](https://github.com/RedHatInsights/vmaas/commit/6759e29aeab60134c516765fc21e489ff8276154))

* fix(csaf): modify csaf_store to reflect new schema ([`2be4213`](https://github.com/RedHatInsights/vmaas/commit/2be42138f5f249c254eca62a8aaee9e44a7b11ca))

* fix(csaf): extend model with CsafProducts ([`5ece339`](https://github.com/RedHatInsights/vmaas/commit/5ece339e5b98a5bdd4d8e0d086cc38133c6cb4bd))

* fix(csaf): handle exceptions when saving files ([`e0efcfd`](https://github.com/RedHatInsights/vmaas/commit/e0efcfd4a88ca0ebbe45efc976e727c097afc449))

* fix(csaf): finalize db schema

RHINENG-7862 ([`7fc6a22`](https://github.com/RedHatInsights/vmaas/commit/7fc6a227b0ae94d9c6936c0960c4e87b4ac6a120))

## v2.56.0 (2024-03-06)

### Feature

* feat(reposcan): add Csaf Store DB insert ([`d73c5ce`](https://github.com/RedHatInsights/vmaas/commit/d73c5ce560683fe12333667455df3dfb850b186a))

## v2.55.1 (2024-02-27)

### Fix

* fix(csaf): set product status id in parser

RHINENG-8391 ([`1955002`](https://github.com/RedHatInsights/vmaas/commit/1955002d66980068e3d21bca713483491c86ecb6))

* fix(csaf): extend model with product status id

RHINENG-8391 ([`7517f1d`](https://github.com/RedHatInsights/vmaas/commit/7517f1dde49ac493dad1eba9622d3fa9e5059347))

* fix(csaf): env var to decide what statuses to parse

RHINENG-8391 ([`8c320fa`](https://github.com/RedHatInsights/vmaas/commit/8c320faf19d4d056d5e766483be2e7e46d62ec07))

## v2.55.0 (2024-02-22)

### Chore

* chore(deps): update vulnerable dependencies

starlette, python-multipart, and cryptography
RHINENG-8390 ([`7d927cf`](https://github.com/RedHatInsights/vmaas/commit/7d927cf96be934631dda627ab0280665103f2ced))

### Feature

* feat: update vmaas-lib

RHINENG-4854 ([`589a11f`](https://github.com/RedHatInsights/vmaas/commit/589a11f4cd700876c9a435602e4eee1908c6cc5d))

### Fix

* fix(webapp-go): unused variable ([`c404a55`](https://github.com/RedHatInsights/vmaas/commit/c404a55e891c118ba595f1e97610a68cd8f3fed7))

## v2.54.2 (2024-02-20)

### Fix

* fix(ephemeral): increase max_stack_depth

RHINENG-8335 ([`6af693d`](https://github.com/RedHatInsights/vmaas/commit/6af693d140ab73b1a2c6bf5f6a6d1c76b795b9e3))

## v2.54.1 (2024-02-15)

### Chore

* chore: check reposcan code with mypy, simplify action with container

RHINENG-7736 ([`27c5aaa`](https://github.com/RedHatInsights/vmaas/commit/27c5aaade286cf72282e2771dbd8caae74b16e52))

### Fix

* fix(metrics): log full endpoint in reposcan but only part of it in webapp

to avoid too many metrics in prometheus ([`293a3e4`](https://github.com/RedHatInsights/vmaas/commit/293a3e4a70e50439bb0778571c38749c8b4351e3))

* fix(metrics): update grafana dashboard with renamed metrics ([`8c4f76d`](https://github.com/RedHatInsights/vmaas/commit/8c4f76decc505f70a2a3f0392646664406400464))

## v2.54.0 (2024-01-29)

### Chore

* chore: don&#39;t sync all csaf files by default ([`ef41296`](https://github.com/RedHatInsights/vmaas/commit/ef412963d5803bf2a3625ca7a6fe7c336bcf7200))

* chore: golang.org/x/crypto to &gt;= 0.17.0 ([`7318287`](https://github.com/RedHatInsights/vmaas/commit/7318287515119780c91c55883e055488c8e097e1))

### Feature

* feat(csaf): parse CSAF JSONs into CsafCves

RHINENG-7697 ([`b2fccaa`](https://github.com/RedHatInsights/vmaas/commit/b2fccaaf3f4944b051fb8d8ff4c7506dafb4fabe))

* feat(csaf): extend csaf models and fix type hints

RHINENG-7697 ([`918745c`](https://github.com/RedHatInsights/vmaas/commit/918745c75abc418df20565c240c35af1b4ae4079))

### Test

* test(csaf): add unit tests for csaf model and parser

RHINENG-7697 ([`b0c0e11`](https://github.com/RedHatInsights/vmaas/commit/b0c0e119e7c236be70be1e36ce436a7825a6a236))

## v2.53.1 (2024-01-24)

### Fix

* fix: implement access log in middleware, allows adding timing info and solves cloudwatch support ([`e41fc94`](https://github.com/RedHatInsights/vmaas/commit/e41fc94f39a4a1ec730e32d1db4934193ac2b72d))

* fix(webapp): middlewares should be stateless to work concurrently ([`7b4ea6b`](https://github.com/RedHatInsights/vmaas/commit/7b4ea6b41c400e792712de3347ab64d1e0957d31))

## v2.53.0 (2024-01-23)

### Feature

* feat(reposcan): add CSAF sync task ([`67c24d2`](https://github.com/RedHatInsights/vmaas/commit/67c24d275f01deff6bf44d3ec8c90f804b9ef800))

## v2.52.0 (2024-01-22)

### Chore

* chore: update python version

RHINENG-7727 ([`2e9b3a3`](https://github.com/RedHatInsights/vmaas/commit/2e9b3a38a89ca2f8457be81963b4f5cec31c9fe9))

* chore: update checkout and setup-python actions ([`46f8412`](https://github.com/RedHatInsights/vmaas/commit/46f841209981d75d1617aa8e991eb0820eec9adc))

* chore: fix code coverage report

RHINENG-7698 ([`2e920bc`](https://github.com/RedHatInsights/vmaas/commit/2e920bc333d14bf3b7adea5c38a93be2d8484e74))

* chore: replace strtobool by custom impl ([`0cb451e`](https://github.com/RedHatInsights/vmaas/commit/0cb451e6156e34ebc763f834af47e080e92c8e22))

### Feature

* feat(csaf): add csaf_ tables needed to store csaf data

RHINENG-6814 ([`96dbd27`](https://github.com/RedHatInsights/vmaas/commit/96dbd278409ca0d35c42073e0cb32a788953a008))

### Refactor

* refactor(webapp): support connexion 3

use AsyncApp instead of AioHttpApp

RHINENG-5883 ([`9790f4f`](https://github.com/RedHatInsights/vmaas/commit/9790f4f6b09ba9554835d1d016512c8fe4ce2f68))

* refactor(reposcan): support connexion 3

use AsyncApp instead of FlaskApp
use apscheduler instead of tornado PeriodicCallback

re-factor subprocess handling

RHINENG-5883 ([`560a1a5`](https://github.com/RedHatInsights/vmaas/commit/560a1a5d78ca839a90d018553bff11d78ff93fd2))

* refactor: upgrade connexion

remove unsupported aiohttp
remove flask
replace tornado PeriodicCallback functionality with apscheduler
install uvicorn as ASGI server

RHINENG-5883 ([`e461019`](https://github.com/RedHatInsights/vmaas/commit/e4610196da13f4966cdea15852da1f4d5b899c59))

## v2.51.0 (2024-01-11)

### Chore

* chore: add len() for batch_list ([`f48fcc1`](https://github.com/RedHatInsights/vmaas/commit/f48fcc1fac255e3f5444db824071b30bfee8b93d))

* chore(deps): add attrs and recreate poetry lock ([`ba77d20`](https://github.com/RedHatInsights/vmaas/commit/ba77d206152449b78212ec7fe66eb745f040f25d))

### Feature

* feat(csaf): add logic for downloading csaf files

RHINENG-6813 ([`6bb6436`](https://github.com/RedHatInsights/vmaas/commit/6bb6436b0cef071da337c83856c7b5d5ad451790))

* feat(csaf): module for storing csaf to db

RHINENG-6813 ([`d0acdc3`](https://github.com/RedHatInsights/vmaas/commit/d0acdc320b329208daa04127d9a7fd2f6f5ed4d8))

* feat(csaf): model collection of csaf files

RHINENG-6813 ([`121fbe4`](https://github.com/RedHatInsights/vmaas/commit/121fbe45ff14a310005c5cde87104e383b1c303a))

* feat(csaf): add csaf_file table

RHINENG-6813 ([`61a2cad`](https://github.com/RedHatInsights/vmaas/commit/61a2cad130bc5437cf8bd263f9e891ced819f9de))

* feat(csaf): add basic metrics

RHINENG-6813 ([`5c5175f`](https://github.com/RedHatInsights/vmaas/commit/5c5175f6a30c374500912071614dee851daa69e1))

### Unknown

* test pr check regarding rbac (#1060)

* test pr check regarding rbac

* Add rbac

* Add dependencies to clowdapp

* Remove unneeded dependencies to clowdapp

* Add rbac as component

* Add vmaas as component

* Add dynaconf variable ([`dea8e6a`](https://github.com/RedHatInsights/vmaas/commit/dea8e6aa17abc171f9d5bfa71141d10be2819c59))

## v2.50.4 (2024-01-09)

### Chore

* chore: migrate from pipenv to poetry ([`6b0fd00`](https://github.com/RedHatInsights/vmaas/commit/6b0fd005149bf8bb187c26136e5c0c963f6f10a8))

* chore: split github workflow steps in tests job ([`8404869`](https://github.com/RedHatInsights/vmaas/commit/84048691c28c0ed1f461661449afe7a7000d59e4))

### Fix

* fix: add required apiPath for app-common-go

vmaas-webapp-go         | field apiPath in DependencyEndpoint: required
vmaas-webapp-go         | panic: runtime error: invalid memory address or nil pointer dereference
vmaas-webapp-go         | [signal SIGSEGV: segmentation violation code=0x1 addr=0x8 pc=0xb9bd3c]
vmaas-webapp-go         |
vmaas-webapp-go         | goroutine 1 [running]:
vmaas-webapp-go         | github.com/redhatinsights/vmaas/base/utils.initDB()
vmaas-webapp-go         | 	/vmaas/go/src/vmaas/base/utils/config.go:71 +0x2c
vmaas-webapp-go         | github.com/redhatinsights/vmaas/base/utils.init.0()
vmaas-webapp-go         | 	/vmaas/go/src/vmaas/base/utils/config.go:63 +0x30
vmaas-webapp-go exited with code 2 ([`d8d4873`](https://github.com/RedHatInsights/vmaas/commit/d8d4873c7d33529c9151bd08dcddd6d49a9fe32f))

## v2.50.3 (2023-11-24)

### Fix

* fix: update vmaas-lib ([`4ea8559`](https://github.com/RedHatInsights/vmaas/commit/4ea855902e2bfa735b2d9d686437023d21d31e4e))

## v2.50.2 (2023-11-23)

### Chore

* chore: remove old cve ignores ([`a0872b4`](https://github.com/RedHatInsights/vmaas/commit/a0872b4cd43de7cdd4a7e9ff39a23376119e3bd5))

* chore: update golang.org/x/net ([`216a7a2`](https://github.com/RedHatInsights/vmaas/commit/216a7a2830ddeefc32ca65d367de032badd4ad11))

* chore: update dependencies ([`21e9fce`](https://github.com/RedHatInsights/vmaas/commit/21e9fce724ca013dfb382144a352a43e5dc65e9a))

### Fix

* fix: update go to 1.20 and update dependencies

go 1.19 is unsupported and go1.20 is already available in ubi8
RHINENG-3785 ([`0103109`](https://github.com/RedHatInsights/vmaas/commit/0103109781bef103f4c6fc8882ba9fbd65e07261))

## v2.50.1 (2023-11-20)

### Chore

* chore: temporary ignore vulnerabilities in pipenv ([`1871dd3`](https://github.com/RedHatInsights/vmaas/commit/1871dd38e20f76379879e3db4ec8710d9d01573e))

### Fix

* fix: use new url for cpe dictionary xml ([`310d3cd`](https://github.com/RedHatInsights/vmaas/commit/310d3cd54b7f56c130f2674f493939b99147f2a8))

## v2.50.0 (2023-10-19)

### Feature

* feat(webapp): return and display latest change of repo in vmaas

RHINENG-2608 ([`8e483ad`](https://github.com/RedHatInsights/vmaas/commit/8e483adebe852c38e161c7d5c7ba1f4d504ec2a7))

## v2.49.1 (2023-10-18)

### Fix

* fix: url returns 404 ([`a7aaac6`](https://github.com/RedHatInsights/vmaas/commit/a7aaac60b730907f01077ab671ee35a1931a1fc3))

## v2.49.0 (2023-10-18)

### Feature

* feat(reposcan): store timestamp of last change of given repository

RHINENG-2608 ([`d2efc4b`](https://github.com/RedHatInsights/vmaas/commit/d2efc4b222a8887e096d2aa2484f82b17e06ca47))

### Unknown

* Adding Security-Compliance Branch Build and Tagging Support (#1048)

Add Security-Compliance Branch Build and Tagging Support. ([`7db1d81`](https://github.com/RedHatInsights/vmaas/commit/7db1d81a819f1eb9b9835f517f5c2df6deb85cc3))

* Fix security vulnerabilities. (#1047)

Upgrade vulnerable packages. ([`9e329b2`](https://github.com/RedHatInsights/vmaas/commit/9e329b2f81af373d9242c1f61abd3254504df348))

## v2.48.5 (2023-08-31)

### Chore

* chore: skip new vulnerabilities ([`5d58325`](https://github.com/RedHatInsights/vmaas/commit/5d583256a21694e3870d645b189c04953f6be5bc))

### Fix

* fix: sort updates also by other fields ([`aa12336`](https://github.com/RedHatInsights/vmaas/commit/aa123365fc64d05a1b88283d4656818513437742))

## v2.48.4 (2023-08-24)

### Chore

* chore: temporary ignore vulnerabilities in pipenv ([`a91e7f6`](https://github.com/RedHatInsights/vmaas/commit/a91e7f6aee413f75041dd8a1f95841b43ebcb376))

### Fix

* fix: consistent affected_packages in vulnerabilities response

VMAAS-1461 ([`41667fd`](https://github.com/RedHatInsights/vmaas/commit/41667fde0d86b456aa6bcc8ea3ade716695fb945))

## v2.48.3 (2023-08-14)

### Chore

* chore: fix new flake8 error ([`b168881`](https://github.com/RedHatInsights/vmaas/commit/b168881bb12e292cca623aea4a33f043734c7bf3))

### Fix

* fix: sorted availableUpdates

RHINENG-1536 ([`b5c176c`](https://github.com/RedHatInsights/vmaas/commit/b5c176c27268761491926e00a8d01d6dd2456be7))

### Unknown

* Re-enable disabled smoke tests ([`cff88fd`](https://github.com/RedHatInsights/vmaas/commit/cff88fda3282620132d60886cd069039addafc6d))

## v2.48.2 (2023-07-20)

### Chore

* chore: upgrade to python-semantic-release 8.x.x ([`c38a7ad`](https://github.com/RedHatInsights/vmaas/commit/c38a7ad676713a0edb078d5dc67b1cef09c28874))

### Fix

* fix: consistent results

https://github.com/RedHatInsights/vmaas-lib/pull/42
VMAAS-1461 ([`c29d8a3`](https://github.com/RedHatInsights/vmaas/commit/c29d8a31104a9d6cc6ed73882a8c092076e9eb29))

## v2.48.1 (2023-07-10)

### Chore

* chore(vmaas-go): promote vmaas-lib ([`ce65f6a`](https://github.com/RedHatInsights/vmaas/commit/ce65f6ad6723b22511ee1180253f0eabd8452b1e))

### Fix

* fix: update gin-gonic to fix CVE-2023-29401

VULN-2713 ([`d1e1c4a`](https://github.com/RedHatInsights/vmaas/commit/d1e1c4a89806b812ee90119588d2a370ff20069d))

## v2.48.0 (2023-07-10)

### Chore

* chore: run golangci-lint only for changes in vmaas-go dir ([`e701693`](https://github.com/RedHatInsights/vmaas/commit/e7016932389b683c6fca034b08da2d99f74fef67))

* chore: remove depguard linter ([`5c49c18`](https://github.com/RedHatInsights/vmaas/commit/5c49c184692b793b8511cfdfabab32a24cd82d40))

* chore: add apiPath to bind APIs to correct paths

VULN-2478 ([`b33bab6`](https://github.com/RedHatInsights/vmaas/commit/b33bab60fddd67dcbb22cddd84635719e49e9edd))

* chore: update flask to fix CVE-2023-30861 and build ([`d6ed82d`](https://github.com/RedHatInsights/vmaas/commit/d6ed82d046f233e7e0aed3947f509dbab78d0c1b))

* chore: improve vmaas-lib config ([`6c48d2b`](https://github.com/RedHatInsights/vmaas/commit/6c48d2b4cd1a8fa0c9853d79006b88e0429cc648))

### Feature

* feat: show package_name and evra in updates response

and bump vmaas-lib
VMAAS-1458 ([`2f9ebcc`](https://github.com/RedHatInsights/vmaas/commit/2f9ebcc660eeb388ec80f1963e00ac4253a790c4))

### Unknown

* Update requests to address pyup vuln 58755 ([`ba6283a`](https://github.com/RedHatInsights/vmaas/commit/ba6283a36c6ff1c1da1eef7dd5ad626820e9a29c))

## v2.47.0 (2023-06-05)

### Feature

* feat: remove &amp; replace old Slack notifications

VMAAS-1455 ([`e15e077`](https://github.com/RedHatInsights/vmaas/commit/e15e07771f7525b0090a23fa343c84f2e5cc7bb0))

## v2.46.2 (2023-05-31)

### Chore

* chore: run golangci-lint ([`823e45e`](https://github.com/RedHatInsights/vmaas/commit/823e45e16fd1e5677328b56def3cc52da90c4df6))

* chore: update go1.19 and dependencies ([`7c90ac2`](https://github.com/RedHatInsights/vmaas/commit/7c90ac2b9cb0ba9fc35a1b6de9f7f2deb3c76ba2))

### Fix

* fix(vmaas-go): add GOMEMLIMIT to remove GOGC workaround for avoiding OOMKill ([`17939d2`](https://github.com/RedHatInsights/vmaas/commit/17939d2ddff0895201e68a4dd9aeb267965cce02))

### Unknown

* Revert &#34;chore: webapp-go doesn&#39;t support OVAL_UNFIXED_EVAL_ENABLED flag&#34;

This reverts commit 8145b47c3c06b7b661c8fec3ccaab5f87b824f57. ([`1e9214f`](https://github.com/RedHatInsights/vmaas/commit/1e9214f3eb0204c48c3af9c238e1b12fefb0080d))

## v2.46.1 (2023-05-31)

### Chore

* chore: add vmaas-go metrics to dashboard ([`7f6f44f`](https://github.com/RedHatInsights/vmaas/commit/7f6f44fb6e86828a567f8594028e99936046f2db))

* chore: change minReplicas -&gt; replicas

minReplicas is deprecated ([`012180c`](https://github.com/RedHatInsights/vmaas/commit/012180c6b806359028b3a0ad8f4d5c8a1943a8e5))

* chore: remove custom probes for webapp-go ([`a67ea50`](https://github.com/RedHatInsights/vmaas/commit/a67ea50c02ab4d62cf0853c4876364b11b134d89))

* chore: run webapp-go by default in environments ([`96cb084`](https://github.com/RedHatInsights/vmaas/commit/96cb0845385f8b089c2e3dc17bff535c59c88364))

* chore: switch OVAL_UNFIXED_EVAL_ENABLED default to TRUE ([`923a5a6`](https://github.com/RedHatInsights/vmaas/commit/923a5a6651833acffca72c7c990f8bc41ce7a589))

* chore: webapp-go doesn&#39;t support OVAL_UNFIXED_EVAL_ENABLED flag ([`8145b47`](https://github.com/RedHatInsights/vmaas/commit/8145b47c3c06b7b661c8fec3ccaab5f87b824f57))

* chore: check if podman/docker is usable ([`0c85c98`](https://github.com/RedHatInsights/vmaas/commit/0c85c98addbcaa88179b1d47912cf9a0a11b1fe9))

* chore: drop webapp_utils and refresh Pipenv lock ([`62b5e8b`](https://github.com/RedHatInsights/vmaas/commit/62b5e8b48da16ea02fa09185a678ef2805dd7ca2))

* chore: none driver doesn&#39;t work as expected, use non-default profile ([`3016d11`](https://github.com/RedHatInsights/vmaas/commit/3016d116eef087e8c30840132805a0a3e62cbc34))

* chore: use different approach to connect from vuln-engine ([`426ad0a`](https://github.com/RedHatInsights/vmaas/commit/426ad0a9d9b27bad97a2bcbec5ac5eea64518496))

### Fix

* fix: return 400 if processing of packages or modules fails ([`cce1136`](https://github.com/RedHatInsights/vmaas/commit/cce11365623eebdc0a6738f6545c68bdf17b02f3))

## v2.46.0 (2023-05-16)

### Feature

* feat: add epoch_required request option

return error if pkg epoch is required and any pkg in request is missing epoch

RHINENG-390 ([`44bf2d3`](https://github.com/RedHatInsights/vmaas/commit/44bf2d33ddeba8827a87a0c8fa17f8bcd7d8e748))

## v2.45.2 (2023-05-15)

### Fix

* fix: use standardized compare func

this custom py implementation is buggy sometimes

{
  &#34;package_list&#34;: [&#34;libxml2-0:2.9.1-6.0.3.el7_9.6.x86_64&#34;],
  &#34;repository_list&#34;: [&#34;rhel-7-server-rpms&#34;]
} ([`12fa9b2`](https://github.com/RedHatInsights/vmaas/commit/12fa9b259ec2bc2d6488ff9d603e6567b3b11e6b))

* fix: backport current package module detection to py ([`ed022a1`](https://github.com/RedHatInsights/vmaas/commit/ed022a127ea038752bfa07753512d6e9421e6ac9))

* fix: backport changed order evaluation (unfixed, fixed) to py ([`7631038`](https://github.com/RedHatInsights/vmaas/commit/76310389503b44a1692c932ab36c109b0c8b58b1))

## v2.45.1 (2023-05-15)

### Fix

* fix(modules): package from module with disabled repo ([`aa79953`](https://github.com/RedHatInsights/vmaas/commit/aa79953c89441d1b6eedba9661957aacedaca2b6))

## v2.45.0 (2023-05-10)

### Feature

* feat(oval): show package name, evra, cpe for unpatched cves

VMAAS-1454 ([`48f5c03`](https://github.com/RedHatInsights/vmaas/commit/48f5c03932a13d683522db3b6313b1b48360e103))

## v2.44.0 (2023-05-09)

### Feature

* feat(oval): unpatched cves take precedence ([`83e1d3b`](https://github.com/RedHatInsights/vmaas/commit/83e1d3bb9314d9282339eea02f8d28ab581ca916))

## v2.43.1 (2023-05-03)

### Fix

* fix(webapp-go): oval and modules fixes

oval: Check module stream in evaluateModuleTest (20be8ac)
oval: Remove duplicates from UnpatchedCves list (9c48307)
modules: Find updates in modular errata for package from module when module is enabled (cd99eef) ([`1b7b69f`](https://github.com/RedHatInsights/vmaas/commit/1b7b69fe529125048e98679c6e8b1fe798fd2485))

## v2.43.0 (2023-04-20)

### Chore

* chore: disable tests which needs to be fixed ([`97b3ed4`](https://github.com/RedHatInsights/vmaas/commit/97b3ed423aebbfb4c9200bc49fa35c134a9ad5b8))

* chore: change to single quotes to fix test run on macos ([`bdf073c`](https://github.com/RedHatInsights/vmaas/commit/bdf073cc7d50d6aba89aa652ffe6707bb75e02a9))

### Feature

* feat: always use optimistic updates, also for known packages

VMAAS-1394 ([`f0d4437`](https://github.com/RedHatInsights/vmaas/commit/f0d4437e1417a660fc3b354c4edfcd2f8be4a150))

### Unknown

* chore(vmaas-go) adjust cpu limit and gomaxprocs ([`b31febf`](https://github.com/RedHatInsights/vmaas/commit/b31febf35a33da02a8634af99d2f8da13fad6e4c))

## v2.42.4 (2023-04-03)

### Fix

* fix(vmaas-go): modules_list consistency with python ([`b136588`](https://github.com/RedHatInsights/vmaas/commit/b1365886e224e065a1162cca7cc08ac160346b52))

## v2.42.3 (2023-03-30)

### Fix

* fix(vmaas-go): don&#39;t gzip response from python vmaas ([`6322d12`](https://github.com/RedHatInsights/vmaas/commit/6322d1236f78a114ecb1777eaf2990f15ecc0cd8))

## v2.42.2 (2023-03-30)

### Chore

* chore: VMAAS_ENV is now copy of ENV_NAME ([`59301a0`](https://github.com/RedHatInsights/vmaas/commit/59301a09faaaea7859eb5c7920304e860d8efc9d))

### Fix

* fix(vmaas-go): bump to vmaas-lib with fixed locking ([`1f9d720`](https://github.com/RedHatInsights/vmaas/commit/1f9d7206debb181787ae05b7b36998d84013ab58))

## v2.42.1 (2023-03-29)

### Chore

* chore: don&#39;t deploy webapp-go by default yet

enable in each env explicitly ([`770b072`](https://github.com/RedHatInsights/vmaas/commit/770b072acf2d1b5025e126e3d5def3e84e8d8014))

* chore(webapp): catch and log all other errors in timer

they are logged when app exits otherwise ([`b7f6ea0`](https://github.com/RedHatInsights/vmaas/commit/b7f6ea0115a3d99dca5291e0d362c6f9d1085f13))

### Fix

* fix(webapp): SSL context usage ([`cb98723`](https://github.com/RedHatInsights/vmaas/commit/cb98723577148d9b65b85407576aeb46c704f405))

## v2.42.0 (2023-03-29)

### Chore

* chore(vmaas-go): bump vmaas-lib to 0.4.0 ([`fe5ae35`](https://github.com/RedHatInsights/vmaas/commit/fe5ae35221bb17c30419b9c61b1f6eae6675a3e8))

* chore(vmaas-go): re-use logging logic from patchman

Co-authored-by: Michael Mraka &lt;michael.mraka@redhat.com&gt; ([`d158cdd`](https://github.com/RedHatInsights/vmaas/commit/d158cdd6bb9b363a8df13f78bda73cc12dabd43d))

* chore(vmaas-go): update vmaas-lib to stream dump to file ([`d1b3353`](https://github.com/RedHatInsights/vmaas/commit/d1b3353e67bef7ba3ca3bf42da0b47769a5585b6))

* chore(vmaas-go): set default cache refresh to 1m ([`0016b72`](https://github.com/RedHatInsights/vmaas/commit/0016b721c8be2cc6a34a39d6a5ede227b040e0c0))

### Feature

* feat(webapp): support many erratas for manually fixable cve ([`54b7099`](https://github.com/RedHatInsights/vmaas/commit/54b709947f930cfaa3447df37107f9dfe4927479))

* feat(webapp): include errata for manually fixable cves ([`e811912`](https://github.com/RedHatInsights/vmaas/commit/e8119125b58ed36cec2b9a3423c80eb01534100e))

* feat(reposcan): add oval_definition_errata to cache ([`9a16df6`](https://github.com/RedHatInsights/vmaas/commit/9a16df619d8cf7ac4a103b3da9fba85cf4c925ef))

## v2.41.1 (2023-03-28)

### Chore

* chore: update clowdapp params to stage defaults ([`a919cb1`](https://github.com/RedHatInsights/vmaas/commit/a919cb1a71d0c1410a10d2f3db7a5880e4e13f60))

### Fix

* fix: docker-compose build ([`25e44da`](https://github.com/RedHatInsights/vmaas/commit/25e44da7856cb52960dc492c0a14ffcbb1482ef2))

* fix: handle exception when sending slack notification ([`7379d2a`](https://github.com/RedHatInsights/vmaas/commit/7379d2ae7a59dbf69373e0c6b3ffe9bb8f986201))

## v2.41.0 (2023-03-27)

### Chore

* chore: remove websocket occurrences ([`742c3da`](https://github.com/RedHatInsights/vmaas/commit/742c3da8b260dd1e2c0b88b168bafdc53f702589))

* chore: add instructions how to copy database from openshift ([`b13ea25`](https://github.com/RedHatInsights/vmaas/commit/b13ea255dda3ecfcff8b3e87541575629eb06955))

* chore: remove generic docker setup and obsolete openshift steps ([`a9770ff`](https://github.com/RedHatInsights/vmaas/commit/a9770ff485f79d57041803b4dfe751d2c4a723fb))

* chore(vmaas-go): remove unused websocket url ([`b60486e`](https://github.com/RedHatInsights/vmaas/commit/b60486e4668ae36e824f4ef9e195c78ac717c249))

* chore: use nginx to serve dump files

reposcan webserver is single-threaded and serving large files is causing timeouts ([`9f79857`](https://github.com/RedHatInsights/vmaas/commit/9f798575e4b6c1b213169f30e60cb7ed5fffe968))

### Feature

* feat(webapp): use timer instead of websocket to refresh data ([`4e14fa7`](https://github.com/RedHatInsights/vmaas/commit/4e14fa7db8511b4a09238ea6ca2b487f9dcebc2a))

## v2.40.0 (2023-03-14)

### Chore

* chore: pylint fixes ([`d5b3c61`](https://github.com/RedHatInsights/vmaas/commit/d5b3c61692cca54e023693733c17ae788de704aa))

* chore: update app-common libs ([`eefc8e1`](https://github.com/RedHatInsights/vmaas/commit/eefc8e105f0b1c191ee68493ea8b265fe70e2ad9))

* chore: replace rsync with http ([`350bd9c`](https://github.com/RedHatInsights/vmaas/commit/350bd9ccef4efc19f8aa65b1167dd3558739b23e))

* chore: temporarily ignore vulnerability 53048 ([`534c002`](https://github.com/RedHatInsights/vmaas/commit/534c0026074dc782074da20a9ecec9db71fb5eec))

* chore(reposcan): use repolist from static path in image in FedRAMP deployment ([`c76d96a`](https://github.com/RedHatInsights/vmaas/commit/c76d96a2ccb8399e5d08f913564d84206c6b289c))

* chore: build repolist to the image ([`739c7a7`](https://github.com/RedHatInsights/vmaas/commit/739c7a7f69b5c08a08f8921b37a8c8bf3d954a61))

* chore(reposcan): deprecate pkgtree generation ([`c2d0c56`](https://github.com/RedHatInsights/vmaas/commit/c2d0c56c08ca37d593b153b156f182f385e18fbd))

* chore: downgrade do ubi8 but with Python 3.9 ([`78fcfb7`](https://github.com/RedHatInsights/vmaas/commit/78fcfb759b786482aa4933795f41282796b775cb))

### Feature

* feat(fedramp): use tls for outgoing connections and simplify config

RHINENG-95

TODO: investigate how to use TLS with rsync ([`e3e9e71`](https://github.com/RedHatInsights/vmaas/commit/e3e9e719bb97b4f904e45af14d6d8b5b5a7281fb))

### Fix

* fix(fedramp): set tls ca for dump download ([`7d27e62`](https://github.com/RedHatInsights/vmaas/commit/7d27e620206c54e5b4f10cce6ffc0f84effe1f42))

### Test

* test: fix tests by specifying db password ([`c489e6f`](https://github.com/RedHatInsights/vmaas/commit/c489e6faaef23e13e1d51344d53515b005bef5ab))

## v2.39.3 (2023-02-17)

### Chore

* chore: don&#39;t run iqe tests against vmaas-go

VMAAS-1439 ([`b798351`](https://github.com/RedHatInsights/vmaas/commit/b7983519db8158c4ce9373eb6435e4164cb45b00))

### Fix

* fix(vmaas-go): incorrect json field for third_party updates

SPM-1869 ([`eb39dba`](https://github.com/RedHatInsights/vmaas/commit/eb39dba5f82f97135085b4ca11af637f37e7daef))

* fix(vmaas-go): return errata: [] instead of null

VMAAS-1447 ([`23908a8`](https://github.com/RedHatInsights/vmaas/commit/23908a8f96282377c3751ae8ff8acb34b0875572))

* fix(vmaas-go): panic during refresh

VMAAS-1446 ([`5d2f900`](https://github.com/RedHatInsights/vmaas/commit/5d2f9001de52e89af17e698c14c0ec8a7dc53312))

## v2.39.2 (2023-01-23)

### Fix

* fix: inconsistent response for invalid packages

update for single invalid package (erp-handler-0:-.i386) returns:
  &#34;update_list&#34;: {
    &#34;erp-handler-0:-.i386&#34;: {}
  }

but when there are 2 invalid packages in the request, (&#34;package_list&#34;: [&#34;cel-handler-0:-.i386, erp-handler-0:-.i386&#34;]) then it returns 400.
the expected response is:
  &#34;update_list&#34;: {
    &#34;cel-handler-0:-.i386&#34;: {},
    &#34;erp-handler-0:-.i386&#34;: {}
  } ([`cdf3f48`](https://github.com/RedHatInsights/vmaas/commit/cdf3f488174c9a10ae65e1cc6b0c18fdc33475a8))

## v2.39.1 (2023-01-20)

### Fix

* fix: allow null repository_list

VULN-2519 ([`0dc8546`](https://github.com/RedHatInsights/vmaas/commit/0dc8546191054bec26832c2338829226789406f4))

## v2.39.0 (2023-01-13)

### Feature

* feat(vmaas-go): use goroutines

VMAAS-1436 ([`6859dca`](https://github.com/RedHatInsights/vmaas/commit/6859dca4da5863c528d68494cdd07de3e4e8f639))

## v2.38.2 (2023-01-10)

### Fix

* fix: watchtower params ([`02ccf10`](https://github.com/RedHatInsights/vmaas/commit/02ccf1026592dfc42b1a0b763fcfb9667d0e04cb))

## v2.38.1 (2023-01-09)

### Fix

* fix(vmaas-go): incorrect cve-errata mapping ([`56094cf`](https://github.com/RedHatInsights/vmaas/commit/56094cffee0ffaff4b4e7218af51a03b69f9f2d6))

## v2.38.0 (2023-01-09)

### Chore

* chore: test failures and  minor changes recommended by pylint ([`6c9e552`](https://github.com/RedHatInsights/vmaas/commit/6c9e5522f4408a62991206b03e42f6e3db83ab6a))

* chore(pylint): add slack notification post timeout ([`064b858`](https://github.com/RedHatInsights/vmaas/commit/064b858061544a5052799b9b3b4e3a33a78c5ea0))

* chore: update pylintrc ([`2b267a9`](https://github.com/RedHatInsights/vmaas/commit/2b267a90d2bbf996af75a8a6e929516e6e1c588b))

### Feature

* feat: use ubi9, python3.9, go1.18

VMAAS-1443 ([`c3e3b60`](https://github.com/RedHatInsights/vmaas/commit/c3e3b602fc8c6731bed14550cde967c5287cb495))

## v2.37.11 (2023-01-05)

### Chore

* chore(pipenv): ignore new vulns for now ([`663ea90`](https://github.com/RedHatInsights/vmaas/commit/663ea90fa87866a0804b24c8d55cd9fbd6b1570a))

### Fix

* fix(vmaas-go): cache reload, adjust GOGC ([`3ab6317`](https://github.com/RedHatInsights/vmaas/commit/3ab6317ef2c2f5547729f78553adf897fa9d46f3))

## v2.37.10 (2022-12-19)

### Chore

* chore: replace deprecated set-output command

VMAAS-1440 ([`eae365c`](https://github.com/RedHatInsights/vmaas/commit/eae365cb3d2cbe78d6f049f0722dd27b9ce0fe89))

### Fix

* fix(vmaas-go): update vmaas-lib and set GC ([`6572ef5`](https://github.com/RedHatInsights/vmaas/commit/6572ef513ae21f909cdbc0109f54c57d85b2306c))

## v2.37.9 (2022-12-15)

### Fix

* fix(vmaas-go): optimizations ([`8d2639c`](https://github.com/RedHatInsights/vmaas/commit/8d2639cda988217648216d6aff5421a92fdd1131))

## v2.37.8 (2022-12-12)

### Fix

* fix(vmaas-go): updates when releasever in repo is empty ([`80c86c0`](https://github.com/RedHatInsights/vmaas/commit/80c86c0fa5e41a4b8a3e6333a2b7328812f5818d))

## v2.37.7 (2022-12-08)

### Fix

* fix(vmaas-go): bump vmaas-lib version to fix arch compatibility ([`ecbd93a`](https://github.com/RedHatInsights/vmaas/commit/ecbd93a022662f0d79e1bf4edfe0cb2868cb231f))

## v2.37.6 (2022-12-08)

### Chore

* chore: update vmaas-go deps ([`01c0803`](https://github.com/RedHatInsights/vmaas/commit/01c0803d01d1bc05726f3703ba2556a7af2742a7))

### Fix

* fix(vmaas-go): add metrics

VMAAS-1437 ([`daf67c0`](https://github.com/RedHatInsights/vmaas/commit/daf67c0c6731b7bcb17f2d3952b50faa9776b8df))

### Test

* test(vmaas-go): probe test ([`8c73ffa`](https://github.com/RedHatInsights/vmaas/commit/8c73ffae7c2bed9aaeee1a03831468a2fa46bbe8))

## v2.37.5 (2022-12-07)

### Chore

* chore(vmaas-go): update vmaas-lib ([`16901cf`](https://github.com/RedHatInsights/vmaas/commit/16901cfa10dcda729be13dde5ed0709dae0b0ff0))

### Fix

* fix(vmaas-go): recover from panic and respond 500 ([`09be0db`](https://github.com/RedHatInsights/vmaas/commit/09be0db507bf35ad9a32241beb9ae47e820858eb))

## v2.37.4 (2022-11-25)

### Fix

* fix(vmaas-go): don&#39;t proxy request when error is present ([`6c86060`](https://github.com/RedHatInsights/vmaas/commit/6c86060465d95830b866e405bcdb5b5aa719a93e))

## v2.37.3 (2022-11-25)

### Fix

* fix(vmaas-go): return 503 during cache reload

VMAAS-1438 ([`6913cc9`](https://github.com/RedHatInsights/vmaas/commit/6913cc9b7a734db169c063c3d9bbe68d0a44d412))

## v2.37.2 (2022-11-24)

### Fix

* fix: define cpu/memory limit/requests separately ([`22a96d9`](https://github.com/RedHatInsights/vmaas/commit/22a96d96015a1d3a0d7ece3d317a3a333a35852d))

## v2.37.1 (2022-11-23)

### Chore

* chore: bump python version in tests ([`47cd2ef`](https://github.com/RedHatInsights/vmaas/commit/47cd2ef9978d12e66b8882fa32d18a3091a8dbe7))

* chore(vmaas-go): don&#39;t block on cache load ([`05db4bc`](https://github.com/RedHatInsights/vmaas/commit/05db4bce20a0d626ed8d6b8d8137870c995ecfcb))

### Fix

* fix(probes): define custom probes ([`7a5c438`](https://github.com/RedHatInsights/vmaas/commit/7a5c4384f4f5e811cfb263817d9ec328869a4179))

## v2.37.0 (2022-11-22)

### Feature

* feat(vulnerabilities): vulns by repository_paths

Provide an option to look up vulnerablities by providing
repository paths (as an addition to repository labels).

This should support tracking updates and vulnerabilities within RHUI
enabled machines, as it would not be dependent on repository labels.

VULN-2443 ([`985ad04`](https://github.com/RedHatInsights/vmaas/commit/985ad04c243e9569b46327813f567cdb303dd087))

* feat(updates): look up updates by repository paths

Provide an option to look up updates by providing repository paths
(as an addition to repository labels).

This should support tracking updates and vulnerabilities within RHUI
enabled machines, as it would not be dependent on repository labels.

VULN-2443 ([`5ce94f0`](https://github.com/RedHatInsights/vmaas/commit/5ce94f082c29d9bb64025d65be2f39a12622c7b2))

* feat(cache): repository id by path

Cache repository ids by path from parsed from their URL.
This is to enable RHUI machines support, which use different repository
labels.

VULN-2443 ([`47bc078`](https://github.com/RedHatInsights/vmaas/commit/47bc07893f90d352dd8cb2be2f974eba123ba70e))

### Fix

* fix(updates): repository_paths used alone

Allow to use `repository_paths` parameter with updates API without
specifying `repository_list`. Otherwise it would use all avilable
repostiories if `repository_list` is not provided.

VULN-2443 ([`2cac2b4`](https://github.com/RedHatInsights/vmaas/commit/2cac2b4a28f00cba3f9d01f11e568e3327c4636a))

### Refactor

* refactor(updates): all repositories as list

VULN-2443 ([`cff6d71`](https://github.com/RedHatInsights/vmaas/commit/cff6d711c1bfcefe2437389bfb700c32efffc786))

* refactor(tests): split cache tests and create fixtures

VULN-2443 ([`2032c21`](https://github.com/RedHatInsights/vmaas/commit/2032c2135b4a86f3bb1eb2e35286ce2585f2a539))

### Test

* test(modularity): robust assertions

Make some assertion robust to expect updates for the same package from
more than one erratum.

VULN-2443 ([`fece842`](https://github.com/RedHatInsights/vmaas/commit/fece8426e9e19e587597780c10fff2a5fc0c13ca))

## v2.36.0 (2022-11-22)

### Chore

* chore(vmaas-go): run PR check

VMAAS-1431 ([`858cdf6`](https://github.com/RedHatInsights/vmaas/commit/858cdf6c067feca35650ac32aefedf6519685df6))

### Feature

* feat(webapp-go): build and deployment

VMAAS-1431 ([`5ab7743`](https://github.com/RedHatInsights/vmaas/commit/5ab7743bd8a3d289d0d4e14a5b9e5a1adf62c137))

* feat(webapp-go): local config

VMAAS-1431 ([`b01edf3`](https://github.com/RedHatInsights/vmaas/commit/b01edf39917cc917771c54be8299311c7f11639b))

* feat(webapp-go): app handling updates and vulnerabilities

VMAAS-1431 ([`c7436c1`](https://github.com/RedHatInsights/vmaas/commit/c7436c1b2e54b5c204116a711c611e05ab5f3fb2))

* feat(webapp-go): base and utils based on redhatinsights/patchman-engine

VMAAS-1431 ([`133b098`](https://github.com/RedHatInsights/vmaas/commit/133b098c1f124ff0d5d812a6772fe397259ad736))

## v2.35.4 (2022-11-14)

### Chore

* chore: remove unused file ([`7be05c8`](https://github.com/RedHatInsights/vmaas/commit/7be05c8031fe40a2d88376251f2d6d9105918a28))

### Fix

* fix(tests): test env vars unqoted

Quotes in Linux when setting env vars are taken as literals.
This also fixes use with podman-compose and direct runs within the test
container.

VULN-2443 ([`4800058`](https://github.com/RedHatInsights/vmaas/commit/4800058fcbdfdae4d15049602d10905fcf9a62d4))

* fix(tests): skip unrelated pipenv check

VULN-2443 ([`bfe0a7b`](https://github.com/RedHatInsights/vmaas/commit/bfe0a7ba750db0ba4e323e96fa362530e7dbee0b))

## v2.35.3 (2022-10-07)

### Fix

* fix(reposcan): collect prometheus metrics from child processes

VMAAS-992 ([`4c16942`](https://github.com/RedHatInsights/vmaas/commit/4c16942abe5817c5a479d46f14d0ec7805d15afd))

## v2.35.2 (2022-07-19)

### Chore

* chore: revert remove dump files in old format changes

the problem was resolved

This reverts commit 302c11c5c70d10c5343b3803064e68cc151e6d0b.
This reverts commit d3e19f1b3a6054ca9e58ad27217e614eda7adec8. ([`9924b21`](https://github.com/RedHatInsights/vmaas/commit/9924b21f230993b06918a89fff0551b98a9d819d))

* chore: remove dump files in old format even in case of error ([`eded3de`](https://github.com/RedHatInsights/vmaas/commit/eded3de4ffe183d2e161a515554d4e8e6b185577))

* chore: remove dump files in old format ([`f6c41dd`](https://github.com/RedHatInsights/vmaas/commit/f6c41dd6eba06040bdc8592011649b951099d8b3))

* chore: rewrite unittest tests to pytest

VMAAS-155 ([`868ab3e`](https://github.com/RedHatInsights/vmaas/commit/868ab3e2b344d76765c2869b5fe25f77390c3b11))

* chore: get repos from RedHatInsights repo ([`d1704b2`](https://github.com/RedHatInsights/vmaas/commit/d1704b2533f963a3e2bacdd03725e69301fd0c13))

* chore: disable pylint lower than 2 . 13 . 0 check ([`5d8344e`](https://github.com/RedHatInsights/vmaas/commit/5d8344e31f633bb8606a94dd0238617bfe17bbd8))

### Fix

* fix: run flake8 in GH actions and fix flake8 issues

VMAAS-1425 ([`ca6d8c1`](https://github.com/RedHatInsights/vmaas/commit/ca6d8c1782a2122a028f247078ab35257c9ab7c9))

## v2.35.1 (2022-05-30)

### Chore

* chore: add repo name prefixes to be stripped ([`6883337`](https://github.com/RedHatInsights/vmaas/commit/688333781f522d50c81c3edbd43c7cdd08220044))

* chore: add PR template ([`6547a6b`](https://github.com/RedHatInsights/vmaas/commit/6547a6b5bd39e699aa3623b078b8f8f5c7dea76c))

* chore: rebasing on top of base branch is now natively available from github UI ([`718b631`](https://github.com/RedHatInsights/vmaas/commit/718b6315513d5da4b53d3015ce90c9938e1b0054))

### Fix

* fix: rename epel repo to epel-8 ([`7b13602`](https://github.com/RedHatInsights/vmaas/commit/7b1360265a1eeba3e35c419b40318d48546138e7))

### Unknown

* VMAAS-1412: pass REPO_NAME_PREFIXES to webapp ([`2244774`](https://github.com/RedHatInsights/vmaas/commit/224477433783d3384e48d38e39afea10bd6aaebe))

## v2.35.0 (2022-03-07)

### Feature

* feat(webapp): Strip prefixes from repository names ([`bcd2572`](https://github.com/RedHatInsights/vmaas/commit/bcd2572de2b192a1b98a8e5b4de91ea7d74b2c87))

### Unknown

* VMAAS-1411: Handle non existing key exception (#959)

* VMAAS-1411: Handle non existing key exception

* VMAAS-1411: Better key check up

Co-authored-by: michalslomczynski &lt;mslomczy@redhat.com&gt; ([`c851f99`](https://github.com/RedHatInsights/vmaas/commit/c851f99984fc9232b2e400963d609f4332b9bb2a))

## v2.34.6 (2022-03-02)

### Fix

* fix(reposcan): fix lint in test_patchlist.py ([`b71de25`](https://github.com/RedHatInsights/vmaas/commit/b71de25e43286e5d39270b70af6844a4d2e42160))

## v2.34.5 (2022-03-01)

### Chore

* chore: special compose for podman is no more needed ([`24757a5`](https://github.com/RedHatInsights/vmaas/commit/24757a5138c89849ac98630fc2096f0887730b6a))

* chore: vmaas_databasefix is no longer needed ([`2686b0f`](https://github.com/RedHatInsights/vmaas/commit/2686b0f2babf3e24659c1f5a37058d1eda84dc3c))

### Fix

* fix(reposcan): handle all other sync exceptions to not skip syncing valid repos ([`9d355da`](https://github.com/RedHatInsights/vmaas/commit/9d355da4f13585c3d9a50ff1220a0e252011cf83))

### Unknown

* VMAAS-1354: Add comment for latest_only to API spec (#962)

Co-authored-by: michalslomczynski &lt;mslomczy@redhat.com&gt; ([`394a60a`](https://github.com/RedHatInsights/vmaas/commit/394a60a2e7d01c611a842349b4848582fb50c2e0))

## v2.34.4 (2022-02-22)

### Chore

* chore(repolist): add rhel 8.1 eus repo ([`af34b38`](https://github.com/RedHatInsights/vmaas/commit/af34b38a3360601d355dd10c243e4700899f2bb4))

### Fix

* fix(local-deployment): official PostgreSQL container has different mount path ([`9fcc693`](https://github.com/RedHatInsights/vmaas/commit/9fcc69332f5bd91189e2918eb86fc1dc534bd331))

## v2.34.3 (2022-02-14)

### Chore

* chore: add missing VMAAS_ENV ([`6e47c1b`](https://github.com/RedHatInsights/vmaas/commit/6e47c1b3598ddbd7bea7c1adbbbd7e79cda7b881))

* chore: add missing slack webhook ([`4a58391`](https://github.com/RedHatInsights/vmaas/commit/4a58391d99460349656892fff8ab4f179f9398d9))

* chore: process repositories in deterministic order ([`6c9b331`](https://github.com/RedHatInsights/vmaas/commit/6c9b3314f9c15c5756f919bdd5dcc25e41c0648b))

### Fix

* fix(reposcan): EUS repos are mapped to CPEs of incorrect EUS version

VMAAS-1414 ([`f9fc5da`](https://github.com/RedHatInsights/vmaas/commit/f9fc5da8b88011bf80637c30131e66598ac2a40e))

## v2.34.2 (2022-02-07)

### Chore

* chore: pylint ([`bfec00d`](https://github.com/RedHatInsights/vmaas/commit/bfec00d2d92115563d8809eed6094b799b7eef74))

* chore: Used CentOS 8 Stream in Dockerfile (Centos 8 EOL) ([`1cccc89`](https://github.com/RedHatInsights/vmaas/commit/1cccc89ee7d8ab278bfc793dce1dead57dfc73d0))

### Fix

* fix(webapp): in errata_associated CVE list include also CVEs found only in OVAL files (missing in repodata due to error)

VULN-1412 ([`4b0157e`](https://github.com/RedHatInsights/vmaas/commit/4b0157ef9994931d16549659efae80339c8c02cd))

* fix(reposcan): don&#39;t delete whole CS when want to delete only repo with null basearch and releasever ([`862c2cb`](https://github.com/RedHatInsights/vmaas/commit/862c2cb67a7a2fd74eed1f86a60d40ff0bb8681d))

## v2.34.1 (2022-02-02)

### Chore

* chore: update pipenv ([`23424f7`](https://github.com/RedHatInsights/vmaas/commit/23424f7177b79b4beafbd053984851accb59312c))

* chore(pr_check): always create artifacts dir ([`eb8a0a6`](https://github.com/RedHatInsights/vmaas/commit/eb8a0a69089ba5ae662891b5eda9213d3d0e9f9d))

* chore(gh-actions): delete integration-tests-local ([`545b007`](https://github.com/RedHatInsights/vmaas/commit/545b0070b9792681ab566d2dbe8fb1fdfcd13747))

### Fix

* fix(reposcan): allow redirects ([`dc433c8`](https://github.com/RedHatInsights/vmaas/commit/dc433c861551b34aec2a2713118fd12c2fefebc7))

## v2.34.0 (2022-01-25)

### Chore

* chore: prometheus metric for count of repos requiring cleanup ([`0b0ec66`](https://github.com/RedHatInsights/vmaas/commit/0b0ec66b316a7ce1961fc0bcc67dd00519aeca90))

* chore: remove legacy service objects

VMAAS-1404 ([`846fc10`](https://github.com/RedHatInsights/vmaas/commit/846fc109149726cfa81c4633267ec52b62701cc8))

### Feature

* feat(reposcan): delete all repos removed from list

VMAAS-1409 ([`e9ec3a8`](https://github.com/RedHatInsights/vmaas/commit/e9ec3a81bb08595a8d3d17168c0b1b26ca5aacfc))

## v2.33.1 (2022-01-21)

### Chore

* chore(tests): sync eus repos for integration tests

VMAAS-1408 ([`45595a7`](https://github.com/RedHatInsights/vmaas/commit/45595a7318c08d505ec5355e736c97e7b7effa99))

### Fix

* fix(webapp): Remove null probes in clowaddp.yaml

- because of clowder upgrade ([`5e38b8d`](https://github.com/RedHatInsights/vmaas/commit/5e38b8dd703fc453285c0d7b36dcc9ff2ee0da19))

## v2.33.0 (2022-01-18)

### Chore

* chore: disable autostart of grafana and prometheus ([`5fd3f37`](https://github.com/RedHatInsights/vmaas/commit/5fd3f3780a591cb6f608b9c1d3d6b9d0647600c3))

* chore: Use vmaas.reposcan.database.upgrade in tests

- include wait_for_services.py into &#34;common&#34; sub-package
- VMAAS-1405 ([`5a9e483`](https://github.com/RedHatInsights/vmaas/commit/5a9e4832ff2278ebd9c639ef64aaea4b060638b9))

* chore: Used offic. docker image for testing db

- VMAAS-1405 ([`abf6e66`](https://github.com/RedHatInsights/vmaas/commit/abf6e663e53cada4be482992031e4c752fcecc92))

* chore: Removed dev database files

- replaced with official postgres container
- VMAAS-1405 ([`abead8b`](https://github.com/RedHatInsights/vmaas/commit/abead8b271364a946c5a35c7c9ae309333eedfae))

### Feature

* feat(webapp): use CPE-repository mapping if available

VMAAS-1402 ([`9e06241`](https://github.com/RedHatInsights/vmaas/commit/9e06241f5b3ac8fb28672154739a7a3afc71380d))

* feat(reposcan): link CPEs with specific repos, not only content sets

VMAAS-1402 ([`428bfad`](https://github.com/RedHatInsights/vmaas/commit/428bfad8e974ae0b0107d7fd557fb842f9b333aa))

## v2.32.11 (2022-01-10)

### Chore

* chore: Remove DB_UPGRADE_SCRIPTS_DIR var from clowdapp.yaml

 - VMAAS-1403 ([`f2e7533`](https://github.com/RedHatInsights/vmaas/commit/f2e7533553ff932713a152bfd5cd42d2790df61e))

* chore: Keep database folder path in container

- VMAAS-1403 ([`9b015d2`](https://github.com/RedHatInsights/vmaas/commit/9b015d2bf66260347a152f1543047f37490e6d51))

* chore: Simplified upgrading test (test_upgrades.py)

- VMAAS-1403 ([`1a144b9`](https://github.com/RedHatInsights/vmaas/commit/1a144b9e9c1779550a5dcddaf55ae5f39b5b080c))

* chore: Made &#34;test_integration.test_phase_2&#34; independent and idempotent

- VMAAS-1403 ([`fdf515c`](https://github.com/RedHatInsights/vmaas/commit/fdf515cc54bac433f1c98c1d60f2d6eb1a1c7ad9))

* chore: Updated reposcan tests (changed db connection)

- VMAAS-1403 ([`7533acb`](https://github.com/RedHatInsights/vmaas/commit/7533acb12d088412f698c6aa3586b76e0ff233c1))

* chore: Updated pylintrc (added no-member) due to rpm.labelCompare issue

- VMAAS-1403 ([`ceffc03`](https://github.com/RedHatInsights/vmaas/commit/ceffc033f8c6759765d931f5259278fe7378347e))

* chore: Refactored testing sql scripts (vmaas/reposcan/test_data/database)

- VMAAS-1403 ([`9c19411`](https://github.com/RedHatInsights/vmaas/commit/9c19411c8a39681a8226b5b245ccfcdff151a154))

* chore: Unified conftest.py, removed redundant files

- VMAAS-1403 ([`1bc41a1`](https://github.com/RedHatInsights/vmaas/commit/1bc41a15ee272ec171fca984b5fcc7844d167174))

* chore: Added common.paths file to define file paths constants

- VMAAS-1403 ([`ef444cd`](https://github.com/RedHatInsights/vmaas/commit/ef444cd94478aa1b7d21076acf39dfd8e31e8114))

* chore: Updated docker-compose.test.yml to use Dockerfile, added db container

- VMAAS-1403
- create db superuser &#34;vmaas_admin&#34; (database/init_schema.sh)
- added testing conf env file (test.env) ([`7854a14`](https://github.com/RedHatInsights/vmaas/commit/7854a1478209499cd224f7f5a53d5a9617e3e3b4))

* chore: Updated &#34;Dockerfile&#34; to be used also for tests

- VMAAS-1403
- removed Dockerfile.test ([`c7c758c`](https://github.com/RedHatInsights/vmaas/commit/c7c758c346f4b69ba1479df0d86b23994e4c04d8))

* chore: use podman to build image from master ([`77fcb6b`](https://github.com/RedHatInsights/vmaas/commit/77fcb6b56bb322cc4e113978193d684abbc2455f))

* chore: use postgresql pkg from RHEL/CentOS

disable unneeded arm64 workarounds

add microdnf opts to not install unneeded packages ([`d5c7e59`](https://github.com/RedHatInsights/vmaas/commit/d5c7e59006469be3102d8c2d54cf6b0cbce789cd))

* chore: improve logging in wait_for_services ([`98c5c4e`](https://github.com/RedHatInsights/vmaas/commit/98c5c4e6362bee1db8b74281f9df95d947690084))

* chore: updated grafana board

- added important signals (traffic rate, latency - overal and per handler)
- added resources usage charts
- added additional charts (containers restarts, RDS usage)
- updated out-of-date queries ([`e061b87`](https://github.com/RedHatInsights/vmaas/commit/e061b8747a36d17d7b314658868e333bce3ef718))

* chore: added grafana config script &#34;scripts/grafana-json-to-yaml.sh&#34; ([`1aa335a`](https://github.com/RedHatInsights/vmaas/commit/1aa335a3064bbba82211d92854a0b160041c9779))

### Fix

* fix(reposcan): Fix vmaas_reader password setting ([`3ac9888`](https://github.com/RedHatInsights/vmaas/commit/3ac98880b8b97cb2d933f78918c370ee37095abf))

### Unknown

* Set private port protocol to tcp for rsync ([`83e93ec`](https://github.com/RedHatInsights/vmaas/commit/83e93ecb739bf1bf6afc22799528fc7c1e92bf9a))

## v2.32.10 (2021-12-08)

### Chore

* chore(webapp): log requests

VMAAS-1395 ([`a9b1c7e`](https://github.com/RedHatInsights/vmaas/commit/a9b1c7e65307433381fc02015d945c62e3a9506a))

### Performance

* perf(webapp): don&#39;t evaluate unfixed CVEs by default now ([`3bec6c8`](https://github.com/RedHatInsights/vmaas/commit/3bec6c8c936b41592c34751a61acb617399f4582))

## v2.32.9 (2021-12-07)

### Chore

* chore(reposcan): add more counters in oval sync

VMAAS-1330 ([`a80071b`](https://github.com/RedHatInsights/vmaas/commit/a80071b2bc2eb2126159d25d75054f55fc59657e))

* chore: renamed env var ([`01b0531`](https://github.com/RedHatInsights/vmaas/commit/01b0531469b126508bb54570c44b0042fc378087))

* chore: process requirements priority labels ([`530ae51`](https://github.com/RedHatInsights/vmaas/commit/530ae51f12e5fe7e0ea3b09bd4da7ccbd66a3c4e))

* chore: requirements are comma,delimited,strings ([`f67cd71`](https://github.com/RedHatInsights/vmaas/commit/f67cd7116a9f3128f67e6880230902b0a0469fe9))

### Fix

* fix(webapp): allow CORS pre-flight check for /cves API

VMAAS-1401 ([`3a7c489`](https://github.com/RedHatInsights/vmaas/commit/3a7c489f5e8f72883522e1237d94611f7917bd1c))

## v2.32.8 (2021-11-25)

### Fix

* fix(websocket): do not advertise None vmaas cache version

VULN-2022 ([`a971fe0`](https://github.com/RedHatInsights/vmaas/commit/a971fe0559c1b55b0a531cbcc29d3c0a6d044cd4))

### Unknown

* Revert &#34;fix(webapp): workaround with appProtocol tcp (clowder hardcodes http) - for istio&#34;

This reverts commit c5341d7cbf3e65cac4abe21bfebd37ebeec61ffe. ([`5640172`](https://github.com/RedHatInsights/vmaas/commit/56401725c2fc9763dfd45b23fabbcd24864f405d))

## v2.32.7 (2021-11-24)

### Fix

* fix(webapp): workaround with appProtocol tcp (clowder hardcodes http) - for istio ([`c5341d7`](https://github.com/RedHatInsights/vmaas/commit/c5341d7cbf3e65cac4abe21bfebd37ebeec61ffe))

## v2.32.6 (2021-11-19)

### Chore

* chore: bump version of development grafana ([`b2f750c`](https://github.com/RedHatInsights/vmaas/commit/b2f750c3083617be64d310cbdc2c48a9e9b3f2f4))

* chore(grafana): fix increase iteration to re-deploy ([`456c21b`](https://github.com/RedHatInsights/vmaas/commit/456c21b1e0e01ebba2f11f0d196e73748ee15bdf))

* chore(grafana): fix container names ([`38cbfdc`](https://github.com/RedHatInsights/vmaas/commit/38cbfdc445dc2860ddfa8d108d5bedef49febb91))

* chore: temporarily disable probes for webapp

until VMAAS-1399 is resolved ([`5bbeac0`](https://github.com/RedHatInsights/vmaas/commit/5bbeac07773c56f005fb0be63948c13df07d64b7))

### Fix

* fix(reposcan): fetch actual data from db progressively

if cache is loaded on start it&#39;s invalid after cascade delete

VMAAS-1397 ([`bbaf703`](https://github.com/RedHatInsights/vmaas/commit/bbaf7039ce048cd2b2c4aa13412ca4140c9a38c8))

* fix(reposcan): add template strings to properly update

VMAAS-1397 ([`60bf563`](https://github.com/RedHatInsights/vmaas/commit/60bf563b93379c9d54566121b05f427c6a2058e0))

* fix(reposcan): use cascade delete to properly delete

it&#39;s easiest solution to make deletions working

also remove old items from cache

VMAAS-1397 ([`74b1c78`](https://github.com/RedHatInsights/vmaas/commit/74b1c784c24cb328cade9b7c260d429e3f273ccd))

## v2.32.5 (2021-11-15)

### Chore

* chore: workaround for broken pipenv ([`eaaa94c`](https://github.com/RedHatInsights/vmaas/commit/eaaa94cf27e766749fb3e35572c84148aee084f2))

* chore: keep pr_check namespace with label ([`760e4c4`](https://github.com/RedHatInsights/vmaas/commit/760e4c4cd5d46053417ecd2e441f4966e12411f1))

### Fix

* fix(reposcan): do not store &#39;None&#39; string if last-modified header is not available

VMAAS-1396 ([`55e908a`](https://github.com/RedHatInsights/vmaas/commit/55e908a44734848c67f03d8e1c39f16c675027b8))

## v2.32.4 (2021-11-12)

### Chore

* chore: VMAAS-1353 modify /packages to retun package name always ([`a1fe7c7`](https://github.com/RedHatInsights/vmaas/commit/a1fe7c7eb883de4a3dc0999785dd3900b7e7b114))

* chore: fix prometheus name ([`9548422`](https://github.com/RedHatInsights/vmaas/commit/954842210e2b00cdc211951371545ba6a48c2848))

* chore: fix github labels in pr_check ([`443315a`](https://github.com/RedHatInsights/vmaas/commit/443315a41904b9666216f5a3eca6b34a077a570a))

* chore: add metrics ports for clowder

VULN-1387 ([`ecb8005`](https://github.com/RedHatInsights/vmaas/commit/ecb800505d0290a7e8a37c7eda4755cb76323a21))

### Fix

* fix(webapp): use common function for parsing evr

VMAAS-1398 ([`0724a04`](https://github.com/RedHatInsights/vmaas/commit/0724a04a8cb97cedef1ddeee26430816c43adbeb))

## v2.32.3 (2021-11-08)

### Chore

* chore: update deps to fix vulnerabilities ([`3018df8`](https://github.com/RedHatInsights/vmaas/commit/3018df8cc0c5230005189c45a35110a06686be88))

### Fix

* fix(webapp): aiohttp 3.8.0 - don&#39;t create new event loop, fix websocket connection ([`2fb0494`](https://github.com/RedHatInsights/vmaas/commit/2fb0494d568fd4c17eb6be3995fee86b306eb3f9))

## v2.32.2 (2021-11-08)

### Fix

* fix(webapp): rebuild index array on cache reload

- VMAAS-1391 ([`9062a6e`](https://github.com/RedHatInsights/vmaas/commit/9062a6e033026e227e2bc075ce99d2d2d5ddf88b))

## v2.32.1 (2021-11-08)

### Chore

* chore: set cvemap url in clowdapp.yaml ([`708f5ae`](https://github.com/RedHatInsights/vmaas/commit/708f5ae6ce82beb625b38996d2404f8d6f3f9c3a))

* chore: temporarily disable probes for webapp ([`5eff3ba`](https://github.com/RedHatInsights/vmaas/commit/5eff3baaad66510911f0f6d34567babd165f1073))

* chore: increase timeout and delay in probes for webapp ([`27f35aa`](https://github.com/RedHatInsights/vmaas/commit/27f35aae537656bd511f7c15c48d4d99f9177224))

* chore: use MEMORY_LIMIT also for webapp requests ([`2f6392e`](https://github.com/RedHatInsights/vmaas/commit/2f6392e06148b9bc7895514fe9ae44e790321f02))

* chore: fix locking script on aarch64 (/tmp unresolvable symlink and need to build psycopg2-binary) ([`885ca30`](https://github.com/RedHatInsights/vmaas/commit/885ca30088c6735d3cde6b5cc3fe1b9f1903d982))

### Fix

* fix(webapp): remove empty release versions from list
VMAAS-1392

fixing
&#34;RHSA-2018:0512&#34;: { ...
 &#34;release_versions&#34;: [ &#34;6.10&#34;, &#34;6.9&#34;, &#34;6ComputeNode&#34;, &#34;6Server&#34;, &#34;6Client&#34;, &#34;6Workstation&#34;, null ]
} ([`77d7267`](https://github.com/RedHatInsights/vmaas/commit/77d72670271c71ddeaf3414c2b47eea7d430acfb))

### Unknown

* Revert &#34;chore: increase timeout and delay in probes for webapp&#34;

This reverts commit 27f35aae537656bd511f7c15c48d4d99f9177224. ([`91af77b`](https://github.com/RedHatInsights/vmaas/commit/91af77b6aebd62f9b7156ea2d2d81245ad8dbc33))

* Revert &#34;chore: temporarily disable probes for webapp&#34;

This reverts commit 5eff3baaad66510911f0f6d34567babd165f1073. ([`973338d`](https://github.com/RedHatInsights/vmaas/commit/973338df139890fa99034849cab5591c9e5b2961))

## v2.32.0 (2021-11-02)

### Chore

* chore(webapp): Added /pkglist endpoint tests

- VMAAS-1391 ([`ca6f867`](https://github.com/RedHatInsights/vmaas/commit/ca6f867c6651f0d7eec51ef40a7c49dc252a4480))

* chore: Cleanup yaml_cache.py, remove useless commented code

- VMAAS-1391 ([`9b6b616`](https://github.com/RedHatInsights/vmaas/commit/9b6b616b9862ca1bd1b512358f95a037cabf6262))

* chore: added testing SQLite cache script, updated test_cache.py

- VMAAS-1391 ([`270dae4`](https://github.com/RedHatInsights/vmaas/commit/270dae4a8020ff03c5216084159db5bca883090f))

* chore: add common.algorithms tests

- VMAAS-1391 ([`e6c60dc`](https://github.com/RedHatInsights/vmaas/commit/e6c60dc4222414d4876a6fbef7a6866b88dd3a4b))

* chore: add test folder to vmaas/common, update module names

rename modules not to conflict with 3rd party libs names
- VMAAS-1391 ([`a523b80`](https://github.com/RedHatInsights/vmaas/commit/a523b802d97d907fb082ebacad6ab5673a040ff0))

### Feature

* feat(webapp): Update api spec with /pkglist endpoint

- VMAAS-1391 ([`0b4aa64`](https://github.com/RedHatInsights/vmaas/commit/0b4aa645d2eb74022366fe7c325cde9b8cb02cd7))

* feat(webapp): Add new /pkglist endpoint

- VMAAS-1391 ([`a542839`](https://github.com/RedHatInsights/vmaas/commit/a542839164d4251bbc03355f99e7634e4ec29f82))

* feat(webapp): Add &#34;package_detail.modified&#34; attribute and modified index to cache

- add modified as int timestamp to store into int array (package_detail)
- add modified index to cache to support &#34;modified_since&#34; argument
- VMAAS-1391 ([`50b1e4d`](https://github.com/RedHatInsights/vmaas/commit/50b1e4d642af0aa1add880de19e43be7f97ef863))

* feat: added common/algorithms.py module with find_index method

- VMAAS-1391 ([`1431ee2`](https://github.com/RedHatInsights/vmaas/commit/1431ee24bad99a38531fd048d5b22df0e4cc70fa))

### Fix

* fix: upgrade db, use utc default timezon for &#34;modified&#34; pkg attribute

- VMAAS-1391 ([`0c96b78`](https://github.com/RedHatInsights/vmaas/commit/0c96b7870b677dd63b3fe3030a47f8c4745867c7))

### Unknown

* feature(test): test errata release_versions
VMAAS-1392 ([`c83f5bd`](https://github.com/RedHatInsights/vmaas/commit/c83f5bd2fb1eec0191981d84614527587630b646))

* feature(webapp): add release_versions into errata API
VMAAS-1392 ([`467ac37`](https://github.com/RedHatInsights/vmaas/commit/467ac3718ba60e3f25da798a4b673862991d132c))

* feature(webapp): store errata id in errata_detail cache
VMAAS-1392 ([`dc57f74`](https://github.com/RedHatInsights/vmaas/commit/dc57f74cfae3af881348cc5ae2052e8091450de2))

## v2.31.2 (2021-10-27)

### Fix

* fix(reposcan): skip populating empty repo data

VMAAS-1378 ([`b7a11b3`](https://github.com/RedHatInsights/vmaas/commit/b7a11b380dd4491d9b24eda4fb3c84af073c1ece))

## v2.31.1 (2021-10-27)

### Chore

* chore: make cpu limit configurable ([`b919f43`](https://github.com/RedHatInsights/vmaas/commit/b919f43453d7ae9370f188bc065d674efe0198b3))

### Fix

* fix(reposcan): Fixed implicit json serialization warning

- in health handler
- vmaas/reposcan/test/test_reposcan.py::TestReposcanApp::test_monitoring_health
  /var/lib/pgsql/.local/share/virtualenvs/vmaas-HvggfB72/lib/python3.6/site-packages/connexion/apis/flask_api.py:199: FutureWarning: Implicit (flask) JSON serialization will change in the next major version. This is triggered because a response body is being serialized as JSON even though the mimetype is not a JSON type. This will be replaced by something that is mimetype-specific and may raise an error instead of silently converting everything to JSON. Please make sure to specify media/mime types in your specs.
    FutureWarning  # a Deprecation targeted at application users.
- VMAAS-1393 ([`7cb9ca0`](https://github.com/RedHatInsights/vmaas/commit/7cb9ca0c807da85b941c374f10a3f0c88fafb0a7))

* fix: Updated lint related things

- VMAAS-1393 ([`0ceacf8`](https://github.com/RedHatInsights/vmaas/commit/0ceacf839df8c687adb04c38e6b1dcd65a5c2290))

* fix: Update deps

- VMAAS-1393 ([`3afb539`](https://github.com/RedHatInsights/vmaas/commit/3afb53966ca4567ba76fc8dd2eff84909f006685))

## v2.31.0 (2021-10-21)

### Feature

* feat(webapp): exclude modified from cache for now ([`c4de51c`](https://github.com/RedHatInsights/vmaas/commit/c4de51cd07e844e4e9770940afc5b77f4551fd4d))

* feat(reposcan): updated package_store test, dump exporter and its tests

VMAAS-1391 ([`5debe20`](https://github.com/RedHatInsights/vmaas/commit/5debe20a723e7ed063b21e0a7cf36ac7a4b7e7a5))

* feat(reposcan): SQL updates - added package.modified timestamp column

VMAAS-1391 ([`08d2b6a`](https://github.com/RedHatInsights/vmaas/commit/08d2b6a877afe2644383c5e6bae8cace179c97dd))

## v2.30.0 (2021-10-07)

### Feature

* feat(webapp): enhance /vulnerabilities API

VMAAS-1382

* adding new manually_fixable_cve_list containing extra CVEs reported by OVAL
* adding extended mode to return also affected packages and advisories (more attributes may be added later)
* obsoleting oval and oval_only modes ([`613125d`](https://github.com/RedHatInsights/vmaas/commit/613125d640769bcb9f556a161c52ce0261bd4597))

### Test

* test: response schema changes ([`ab62a00`](https://github.com/RedHatInsights/vmaas/commit/ab62a00d7c9c6770944ee50eb39733683af82e75))

## v2.29.0 (2021-10-07)

### Feature

* feat(webapp): enable optimistic updates for /vulnerabilities

VMAAS-1386 ([`d7c1fe0`](https://github.com/RedHatInsights/vmaas/commit/d7c1fe03ffff9089dd615e8b028b0ecab8eb309c))

## v2.28.4 (2021-10-07)

### Fix

* fix(webapp): load as many tables as possible even when dump is not up to date ([`751989b`](https://github.com/RedHatInsights/vmaas/commit/751989b6c9256575ac3071fae6bee93be9a4ae9b))

## v2.28.3 (2021-10-06)

### Fix

* fix(webapp): Fix /pkgtree third-party repos info and third-party flag

- Include third-party package repositories - not included before
- Exclude package with third-party repositories if needed
- VMAAS-1351 ([`717d79c`](https://github.com/RedHatInsights/vmaas/commit/717d79c820ed3e7f6b021b58b9cac7501b07225e))

## v2.28.2 (2021-10-05)

### Chore

* chore: use labels in pr_check

VULN-1948 ([`1155152`](https://github.com/RedHatInsights/vmaas/commit/1155152a9fbb13f8095a23835b1622008c01fdfb))

### Fix

* fix(webapp): Fix /pkgtree endpoint when &#34;modified_since&#34; used

- Exclude packages without time info (without errata) when &#34;modified_since&#34; used in request

VMAAS-1346 ([`0f1d73e`](https://github.com/RedHatInsights/vmaas/commit/0f1d73ed3542b94a4cfa35156e941a338e7a7f6d))

## v2.28.1 (2021-09-17)

### Chore

* chore: don&#39;t wait for websocket in init container ([`65b4d41`](https://github.com/RedHatInsights/vmaas/commit/65b4d4197c24d0801e45504c1ded43498ab4f951))

* chore: repolist for multicontext module tests

VMAAS-1383 ([`99403a8`](https://github.com/RedHatInsights/vmaas/commit/99403a8f1e911599be992a5e9b3cf4677f578d95))

### Fix

* fix: set timeout for requests while waiting for services

requests will hang if no timeout is set which causes unnecessary pod restarts just after deploy ([`ab4cb40`](https://github.com/RedHatInsights/vmaas/commit/ab4cb40b791df2e5f9558da664428574c1e9fad5))

## v2.28.0 (2021-09-14)

### Chore

* chore: allow build on aarch64 ([`5ba778f`](https://github.com/RedHatInsights/vmaas/commit/5ba778f4aa03c354bfa72fe80d6c8c5c96bf0327))

* chore: remove unused MANIFEST_* params ([`434a9aa`](https://github.com/RedHatInsights/vmaas/commit/434a9aa37a38be624b0d151086d817746d882128))

* chore: signal handler takes 2 argmuents ([`b37e22d`](https://github.com/RedHatInsights/vmaas/commit/b37e22dced31ebf3758218f8b3e050b305c93936))

* chore(clowder): add proxy for reposcan-service ([`5fe1ac1`](https://github.com/RedHatInsights/vmaas/commit/5fe1ac113f795a55c60a9cbfb5d819848c9b33ce))

### Feature

* feat: delete stream requires when stream is deleted
VMAAS-1377 ([`db18b59`](https://github.com/RedHatInsights/vmaas/commit/db18b59c88057cd7ba9462a3b17e2d2ff2c1a1bf))

* feat: improve exporter test form module requires
VMAAS-1377 ([`dd79c7c`](https://github.com/RedHatInsights/vmaas/commit/dd79c7c3304167280fff939e67272f1df0784196))

* feat: updated test for module loading
VMAAS-1377 ([`e98fca9`](https://github.com/RedHatInsights/vmaas/commit/e98fca94b3307884f10dd7e3c7feee27c9d9433f))

* feat: fiter out module stream without satisfied requires
VMAAS-1377 ([`b0821bc`](https://github.com/RedHatInsights/vmaas/commit/b0821bc3982ded9111e1cb1d841703be0345fad9))

* feat: read module requires into cache
VMAAS-1377 ([`3b4afc7`](https://github.com/RedHatInsights/vmaas/commit/3b4afc72cb875a3200529f1cc288f3f5befa1e7e))

* feat: export module requires data
VMAAS-1377 ([`77b48c6`](https://github.com/RedHatInsights/vmaas/commit/77b48c61e4b8cb65a145a2d24e2db8c3d45fce47))

* feat: store module requires during reposcan
VMAAS-1377 ([`8487e65`](https://github.com/RedHatInsights/vmaas/commit/8487e65d70f8d0ed1357177d734aab2b7af52e37))

* feat: table to store module dependencies
VMAAS-1377 ([`24f3a25`](https://github.com/RedHatInsights/vmaas/commit/24f3a25a0f85edb8c5fc0164832302546e9711eb))

### Fix

* fix: silence pytest warnings

test_repository_store.py:57: PytestUnknownMarkWarning: Unknown pytest.mark.first - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/mark.html ([`c71b03a`](https://github.com/RedHatInsights/vmaas/commit/c71b03ad08223bdff772dc895aeca3c70ed13431))

* fix: update developer setup to single app layout ([`9810bc2`](https://github.com/RedHatInsights/vmaas/commit/9810bc2ea42165ed9cd1c4005dbd45a344e95db2))

## v2.27.2 (2021-09-07)

### Build

* build: remove workaround for postgresql installation ([`374225e`](https://github.com/RedHatInsights/vmaas/commit/374225e47046e45b63b16094b73bf50bf48fcccd))

* build: disable unnecessary repos ([`6a3ed7d`](https://github.com/RedHatInsights/vmaas/commit/6a3ed7d8b014b1d36eb2fa315b67c65b20c17fee))

### Fix

* fix(test): fixing new pylint warnings

W1514: Using open without explicitly specifying an encoding (unspecified-encoding)
C0206: Consider iterating with .items() (consider-using-dict-items)
R1735: Consider using {} instead of dict() (use-dict-literal)
R1732: Consider using &#39;with&#39; for resource-allocating operations (consider-using-with)
W0612: Unused variable &#39;err&#39; (unused-variable)
R0402: Use &#39;from vmaas.common import rpm&#39; instead (consider-using-from-import) ([`024e118`](https://github.com/RedHatInsights/vmaas/commit/024e1186e7534ff7f38a22fda2ee64e11e8bec43))

* fix(test): fix pur deps to fix AttributeError: &#39;bool&#39; object has no attribute &#39;lower&#39;

fixing
Traceback (most recent call last):
  File &#34;/var/lib/pgsql/.local/share/virtualenvs/vmaas-HvggfB72/bin/pur&#34;, line 8, in &lt;module&gt;
    sys.exit(pur())
...
  File &#34;/var/lib/pgsql/.local/share/virtualenvs/vmaas-HvggfB72/lib/python3.6/site-packages/pur/__init__.py&#34;, line 54, in convert
    if value.lower() == &#39;true&#39;:
AttributeError: &#39;bool&#39; object has no attribute &#39;lower&#39; ([`1d73e3b`](https://github.com/RedHatInsights/vmaas/commit/1d73e3b92619afd15d7eb267cbcf869852c8cebe))

## v2.27.1 (2021-09-07)

### Fix

* fix(reposcan): fixed advisory &#34;reboot_suggested&#34; value parsing

VMAAS-1365 ([`85c1ddd`](https://github.com/RedHatInsights/vmaas/commit/85c1ddda23531c9118a7000d711cabae99c47eef))

## v2.27.0 (2021-09-06)

### Feature

* feat(webapp): added &#39;requires_reboot&#39; to api docs (v3)

VMAAS-1365 ([`32440f2`](https://github.com/RedHatInsights/vmaas/commit/32440f2be2bc98fed7486e6dc1f0383923e2cb15))

* feat(webapp): added &#39;requires_reboot&#39; to webapp

VMAAS-1365

updated tests, updated testing cache data ([`f222500`](https://github.com/RedHatInsights/vmaas/commit/f2225000eef4c7a632649ae87695de451d91f6eb))

* feat(reposcan): added &#39;requires_reboot&#39; to dump exporter

VMAAS-1365 ([`309f35e`](https://github.com/RedHatInsights/vmaas/commit/309f35e2d3f6c097c432cac7429dbff4cf905dca))

* feat(reposcan): added option to disable some sync parts (git, cve, oval...)

VMAAS-1365 ([`f38da8e`](https://github.com/RedHatInsights/vmaas/commit/f38da8e14de4143bde3fd310f75166a79f8bc1aa))

## v2.26.1 (2021-09-06)

### Fix

* fix(webapp): fix /updates test for arch &#34;(none)&#34;

VMAAS-1375

It was failing when used with third_party and optimistic_updates ([`c24be27`](https://github.com/RedHatInsights/vmaas/commit/c24be272d61c2e385efbfd9da176c70ae58434bd))

## v2.26.0 (2021-09-03)

### Chore

* chore(clowder): smooth transition with legacy ports

VULN-1909 ([`d06a7aa`](https://github.com/RedHatInsights/vmaas/commit/d06a7aa7f1e802d2d47fca005f79974b7b059ebd))

### Feature

* feat(reposcan): auto delete old oval items

VMAAS-1332 ([`38322bf`](https://github.com/RedHatInsights/vmaas/commit/38322bf6cd48585387d8e25d51f4bf5c7d669988))

### Unknown

* revert: change memory limits in webapp

VULN-1906 ([`8d42a21`](https://github.com/RedHatInsights/vmaas/commit/8d42a218816379c7eef0455e8a28eac856f93f3c))

## v2.25.0 (2021-09-01)

### Build

* build: remove generate_manifest.sh and deps.
VULN-1841 ([`b672578`](https://github.com/RedHatInsights/vmaas/commit/b672578cc79d29359a721453791f11ed7f6ba2f7))

### Chore

* chore: change memory limits in webapp

VULN-1906 ([`4965608`](https://github.com/RedHatInsights/vmaas/commit/4965608a1f5fb1f4f93b66b8b6a985230f888288))

* chore: add rhel8 baseos testing data ([`39e468b`](https://github.com/RedHatInsights/vmaas/commit/39e468b04bfe2c302ff00e8c924962f90b06294b))

* chore: improve image build

VULN-1824 ([`0dc8cd2`](https://github.com/RedHatInsights/vmaas/commit/0dc8cd27468afa41928e4d5caf32b120b2b12490))

### Feature

* feat: implement requires_reboot flag for advisories ([`4a58f6d`](https://github.com/RedHatInsights/vmaas/commit/4a58f6d2d6c76b289d3b1e22aca2fcd0a377679e))

* feat(reposcan): automatically delete filtered/obsolete OVAL streams

VMAAS-1332 ([`bd977e2`](https://github.com/RedHatInsights/vmaas/commit/bd977e210c33a955ef23d0ab8bb7cf5e56533498))

* feat(reposcan): support deleting OVAL files

VMAAS-1332 ([`a499029`](https://github.com/RedHatInsights/vmaas/commit/a49902903fbe075f68aa16dbae3a8bb8c50a9b45))

### Fix

* fix(reposcan): disable rhel-7-alt OVAL stream

VMAAS-1373

see also https://github.com/quay/claircore/commit/baff66333b025d863779cea58e1a5aedd22a4bb3#diff-2f9b764af2192de1953c5744b05da6f02f259381069047cf2cc8e718fdec3b4f ([`2ea9987`](https://github.com/RedHatInsights/vmaas/commit/2ea99875f6038b7fad13fc66e07a2aadf9f45e18))

* fix(database): add missing file_id foreign key ([`a6a23a9`](https://github.com/RedHatInsights/vmaas/commit/a6a23a95feb45a9560fd580ad84f095b6b1a6019))

## v2.24.1 (2021-07-28)

### Chore

* chore: jenkins is replaced by gh action/app-sre pr_check ([`a0a6285`](https://github.com/RedHatInsights/vmaas/commit/a0a6285070f9f1195033963c15c6c978511b02e9))

* chore: run smoke tests using cji

VULN-1742 ([`081a2ac`](https://github.com/RedHatInsights/vmaas/commit/081a2ac0b3263aac7ad1378f7395ede5c5c5df63))

### Fix

* fix(clowder): use rds ca path ([`9f8a568`](https://github.com/RedHatInsights/vmaas/commit/9f8a5684d3dc02641d59926f31e1f4d975ecc274))

## v2.24.0 (2021-07-15)

### Feature

* feat(reposcan): support filtering OVAL files

put a warning in a log ([`29d555c`](https://github.com/RedHatInsights/vmaas/commit/29d555c7c67939e3e37eb3840935bc590b426450))

## v2.23.6 (2021-07-14)

### Chore

* chore: unify logging - use format from vuln-engine ([`f0f7679`](https://github.com/RedHatInsights/vmaas/commit/f0f7679f2d2bfacffb025a184a67df9439e9d6e0))

* chore: use github-vmaas-bot instead of vulnerability-bot ([`fb64e96`](https://github.com/RedHatInsights/vmaas/commit/fb64e9648fcca7cccfbd29bde4c74b6c8fe59a25))

* chore: use github-vulnerability-bot secret from epehemeral-base ([`bbcdbde`](https://github.com/RedHatInsights/vmaas/commit/bbcdbde1fee6aa634f05ce7de415561af9ebeeff))

* chore: clean unnecessary things from clowdapp ([`2840010`](https://github.com/RedHatInsights/vmaas/commit/284001088cc358cadf632bda23576c49ffa63038))

### Fix

* fix(reposcan): fix slow re-syncs due to missing index ([`e9c9499`](https://github.com/RedHatInsights/vmaas/commit/e9c9499970d15a5c5e99be756982ad566724eff4))

### Refactor

* refactor: migrate from configmap to deployment ([`f3b6f31`](https://github.com/RedHatInsights/vmaas/commit/f3b6f31b60348e7aa6594b3af9cbc96e36649783))

## v2.23.5 (2021-07-12)

### Chore

* chore: fix pylint issue, explicit check param is recommended ([`8e5ced5`](https://github.com/RedHatInsights/vmaas/commit/8e5ced53cc3fc4d08fc9a3d4b2edddc0fd891d3c))

### Fix

* fix(reposcan): products being a list instead of dict in reposcan ([`cfba1fd`](https://github.com/RedHatInsights/vmaas/commit/cfba1fd69cd94af0a2c08aa458075f904e3b6bc3))

## v2.23.4 (2021-07-12)

### Chore

* chore(clowder): respect resource requests/limits in ephemeral ([`b76c43c`](https://github.com/RedHatInsights/vmaas/commit/b76c43c351df588fb50208c7e25983cbf5a09d40))

### Fix

* fix: check=True throws subprocess.CalledProcessError in case of non-zero return code ([`cf4cee5`](https://github.com/RedHatInsights/vmaas/commit/cf4cee5e5bf164c9774e9c4ac64feb03b13b3284))

### Unknown

* Fix multiple content-set syncing process ([`433b9f6`](https://github.com/RedHatInsights/vmaas/commit/433b9f628a192727e75cd8decc6074092dbd9742))

## v2.23.3 (2021-07-01)

### Fix

* fix(reposcan): remove parenthesis from returning statement ([`7e54a90`](https://github.com/RedHatInsights/vmaas/commit/7e54a904eeefc11473251ab1c3fc4f614019c8a3))

## v2.23.2 (2021-07-01)

### Chore

* chore: faster table cleanup during migration ([`177115d`](https://github.com/RedHatInsights/vmaas/commit/177115d83b09b9a4a4c92d1b62f4b00bbcfaf761))

### Fix

* fix(database): set ON_ERROR_STOP=on to have non-zero RC when error occurs, also don&#39;t rely on stderr

notices from truncate command are printed to stderr ([`1046e97`](https://github.com/RedHatInsights/vmaas/commit/1046e976680670245eb40ce5f10ed946003b1de7))

## v2.23.1 (2021-07-01)

### Fix

* fix(database): apply migration file as single transaction ([`c64d11f`](https://github.com/RedHatInsights/vmaas/commit/c64d11f7b14411834657a29710ce1d0083976374))

## v2.23.0 (2021-07-01)

### Chore

* chore: improve cleanup speed during migration ([`4fb3f1e`](https://github.com/RedHatInsights/vmaas/commit/4fb3f1e4a3ca7e1627a0a4525c738946122fd57d))

### Feature

* feat(database): bump database to rhel8/centos8 ([`8fc0b23`](https://github.com/RedHatInsights/vmaas/commit/8fc0b23953cb5a97f8accbca057e14f6dd223fd0))

## v2.22.1 (2021-07-01)

### Chore

* chore: remove vmaas-reposcan-tmp persistent storage ([`67e9e35`](https://github.com/RedHatInsights/vmaas/commit/67e9e35dee0a458bb754738774fe03020108757d))

### Fix

* fix(reposcan): detect changes in oval files better

improves incremental updates where oval_id can change ([`c69017a`](https://github.com/RedHatInsights/vmaas/commit/c69017a17f14a2ebdf7e3342bf1cab0d05eba906))

* fix(reposcan): sync OVAL data into updated schema ([`8a39630`](https://github.com/RedHatInsights/vmaas/commit/8a39630b6d6c5e5bc4e4da655157c4a3c7a91622))

* fix(database): re-structure OVAL-file associations ([`c3e2d6b`](https://github.com/RedHatInsights/vmaas/commit/c3e2d6b8374c5d91b91d1f616c840abc82fd9110))

## v2.22.0 (2021-06-17)

### Feature

* feat(reposcan): Accept multiple repolists for git sync ([`f85f4a0`](https://github.com/RedHatInsights/vmaas/commit/f85f4a01b206063b1221de8853b5ce92aa6b30d0))

## v2.21.0 (2021-06-10)

### Chore

* chore: deploy vmaas component of vulnerability app ([`86ddd51`](https://github.com/RedHatInsights/vmaas/commit/86ddd51ef9fac28cb2c84c28b37dd32a4d02c0a7))

### Feature

* feat(reposcan): retry periodic cache dump later if it failed ([`0694e3a`](https://github.com/RedHatInsights/vmaas/commit/0694e3a9f6c15164eeeedd4ce8b918704224681d))

## v2.20.2 (2021-06-09)

### Fix

* fix: bump app_common_python to get sslMode ([`b76eb7f`](https://github.com/RedHatInsights/vmaas/commit/b76eb7f8c70b245da94f5007825b034ec6d4daa5))

* fix: default ssl mode can&#39;t be empty string ([`17a366e`](https://github.com/RedHatInsights/vmaas/commit/17a366e40246c9a9106e06824a4abcccc6cff5f7))

## v2.20.1 (2021-06-08)

### Fix

* fix(webapp): revert: add &#34;modified_since&#34; to /v3/pkgtree response&#34;

This reverts commit aee93a6a20d1bee6a9f4af45d07e1ae6d399c79a. ([`ae15ba0`](https://github.com/RedHatInsights/vmaas/commit/ae15ba02709fca396a6b678fdfdb84f4d0b35ade))

## v2.20.0 (2021-06-02)

### Chore

* chore: fix new pylint issues ([`ce92d78`](https://github.com/RedHatInsights/vmaas/commit/ce92d78856f15ec9f5ce26d728fe299326e3381e))

* chore: podman bindings are not needed + re-gen lock file ([`acee9ef`](https://github.com/RedHatInsights/vmaas/commit/acee9ef3d2d14de58390d45359c1748fe9cc00cc))

* chore: add script to easily re-generate Pipfile.lock ([`3616dd5`](https://github.com/RedHatInsights/vmaas/commit/3616dd5c940d95f4c65d70fb6c02b4e6e7070616))

### Feature

* feat: set PostgreSQL SSL mode ([`b5a555f`](https://github.com/RedHatInsights/vmaas/commit/b5a555f983e32dcb33be29a1a01f3f9b5e5cb32a))

### Refactor

* refactor(webapp): make responses more consistent ([`00447bb`](https://github.com/RedHatInsights/vmaas/commit/00447bb331347c3ec1c7502a198b794edc95fa43))

## v2.19.2 (2021-05-25)

### Fix

* fix(webapp): add &#34;modified_since&#34; to /v3/pkgtree response
- to be consistent with /cves /errata endpoints ([`aee93a6`](https://github.com/RedHatInsights/vmaas/commit/aee93a6a20d1bee6a9f4af45d07e1ae6d399c79a))

## v2.19.1 (2021-05-25)

### Fix

* fix(webapp): comparison between srt and int, enhance split the string to int/str parts

same logic as storing evr_t type in postgres

e.g. failure in comparing microcode_ctl-4:20180807a-2.el8.x86_64 and microcode_ctl-4:20200609-2.20210216.1.el8_3.x86_64 ([`315fee8`](https://github.com/RedHatInsights/vmaas/commit/315fee89628156b83956ddf71df928896d34ee89))

* fix(webapp): if CVE is not in DB from cvemap, it&#39;s not connected with definition ([`d244df0`](https://github.com/RedHatInsights/vmaas/commit/d244df04e69c0b839f8674de9fc638890a0bb92c))

## v2.19.0 (2021-05-19)

### Feature

* feat(webapp): filter modules_list in OVAL evaluation ([`ab8011f`](https://github.com/RedHatInsights/vmaas/commit/ab8011f443a16299aab4f11aaa20f132bd32bb35))

* feat(reposcan): import OVAL module streams ([`0408efc`](https://github.com/RedHatInsights/vmaas/commit/0408efcec808297f09226c648eddb3f11f95279e))

## v2.18.1 (2021-05-17)

### Chore

* chore: fix path in semantic release config ([`3d1fa21`](https://github.com/RedHatInsights/vmaas/commit/3d1fa210f96f5418d4a20448a2ccb95054cce32f))

* chore: Reorganize project files as a Python project ([`fc690ee`](https://github.com/RedHatInsights/vmaas/commit/fc690ee74054c099853a3ff1f71c283266f442da))

### Fix

* fix(reposcan): fix path to wait script and replace it with python version ([`8d40e09`](https://github.com/RedHatInsights/vmaas/commit/8d40e097d31632f0eb505b8de960ede448376117))

## v2.18.0 (2021-05-14)

### Chore

* chore(webapp): start syncing sqlite file instead of shelve

test data need to be re-generated to sqlite format ([`526db5a`](https://github.com/RedHatInsights/vmaas/commit/526db5abc59fcbd3a51a453d0ba9f12849eb552f))

* chore(reposcan): stop generating shelve dump and rewrite exporter test to use sqlite ([`86974d6`](https://github.com/RedHatInsights/vmaas/commit/86974d61c0325ab3f15ee7a63740c1b30a47f4ea))

### Feature

* feat(webapp): return HTTP 503 when no dump is loaded ([`5b7002a`](https://github.com/RedHatInsights/vmaas/commit/5b7002a968c1a12ca7a51c58b9fe1a3e7020468a))

* feat: add sqlite database format

Extract sqlite dump generation code from the semtezv/next branch ([`eedcd53`](https://github.com/RedHatInsights/vmaas/commit/eedcd5330546a53f19894d621c3099b69ec0009c))

### Fix

* fix: third_party support, fix repo/errata/cve structure, updates order, datetime format etc. ([`e0e44a6`](https://github.com/RedHatInsights/vmaas/commit/e0e44a68c2d0b045a7f2aa203c8c36abdccaeea5))

* fix(webapp): load as set() and array.array(&#39;q&#39;) where previously ([`828a5f8`](https://github.com/RedHatInsights/vmaas/commit/828a5f89b9cd7b11ea0dc64f40440628fa753586))

* fix: export and load missing OVAL data ([`b02aa74`](https://github.com/RedHatInsights/vmaas/commit/b02aa74b80d0e87be8fb462100d9872ef1bb21ca))

* fix(reposcan): fix the package_name query ([`27aff01`](https://github.com/RedHatInsights/vmaas/commit/27aff01d12af26cf3d428bcba28d10c93d955e97))

* fix(webapp): productid2repoids was removed ([`3e461ee`](https://github.com/RedHatInsights/vmaas/commit/3e461eebd010825061ce2a53e10a6f243af52887))

* fix: move fetch_latest_dump out of DataDump ([`3b6eb9b`](https://github.com/RedHatInsights/vmaas/commit/3b6eb9bc0429187bcbd9f1c5e7fbc25db2e0ea39))

* fix(reposcan): /data is mount point ([`a2c93b7`](https://github.com/RedHatInsights/vmaas/commit/a2c93b7f2fbd29bf313614b1ae45a4bd173a6400))

## v2.17.0 (2021-05-12)

### Feature

* feat(reposcan): allow repolists to opt_out of default certificates ([`dc00b21`](https://github.com/RedHatInsights/vmaas/commit/dc00b215c1b4d4283f87f9b63a02fa26fcc27aa1))

## v2.16.0 (2021-05-12)

### Feature

* feat(reposcan): accept lists for content set data ([`24be17e`](https://github.com/RedHatInsights/vmaas/commit/24be17ec2ae0ef344eca161556c617cefa95669b))

## v2.15.2 (2021-05-05)

### Fix

* fix(webapp): default to false until it&#39;s well tested, apps can request it anyway using param ([`646b3f6`](https://github.com/RedHatInsights/vmaas/commit/646b3f683a2e5eafd33a2750e0895aa8c4f153bd))

## v2.15.1 (2021-05-04)

### Fix

* fix(webapp): add more as_long_arr casts ([`17d5137`](https://github.com/RedHatInsights/vmaas/commit/17d513726b333445bcbfb012d1c6b0cd913cc100))

* fix(webapp): productid2repoids is not used ([`9483f9d`](https://github.com/RedHatInsights/vmaas/commit/9483f9dc18f113491b1371f472733f0a7c745691))

## v2.15.0 (2021-05-04)

### Feature

* feat(webapp): evaluate OVAL ([`06db2b1`](https://github.com/RedHatInsights/vmaas/commit/06db2b17148e10e3828a065401b57e3baf9800f9))

* feat(reposcan): export OVAL data ([`49b1ec4`](https://github.com/RedHatInsights/vmaas/commit/49b1ec461b8a37d82e2c4fc7edb3b0a714e48cf7))

### Fix

* fix(webapp): warn but don&#39;t crash ([`8f4c0c2`](https://github.com/RedHatInsights/vmaas/commit/8f4c0c294fd877a3e4ec26dac6b92f07db8a1079))

## v2.14.1 (2021-04-29)

### Fix

* fix(reposcan): fix KeyError when importing new repos ([`9303d34`](https://github.com/RedHatInsights/vmaas/commit/9303d347c364757e2af715321c53fb6415939c45))

## v2.14.0 (2021-04-28)

### Feature

* feat(reposcan): Warn about extra repos in DB when syncing main repolist from git ([`5c5693d`](https://github.com/RedHatInsights/vmaas/commit/5c5693df8afc88d9bca0acb6924853ad754b78bc))

### Fix

* fix(reposcan): sync missing package names and EVRs ([`5079858`](https://github.com/RedHatInsights/vmaas/commit/507985819d9b6940debdf5b33080b32762743cbb))

* fix(reposcan): sync CPE substrings from OVAL files ([`605d020`](https://github.com/RedHatInsights/vmaas/commit/605d020a28a8bbaf67f043e24507d87e8739af11))

## v2.13.2 (2021-04-28)

### Chore

* chore: add cached epel repolist for tests ([`685c3a3`](https://github.com/RedHatInsights/vmaas/commit/685c3a3f5c8614dd61cd65a1a3a5e76866848089))

### Fix

* fix(reposcan): optimize content deletion speed ([`b5fee66`](https://github.com/RedHatInsights/vmaas/commit/b5fee6630ec249bd89ee4b82da0edb875902edb6))

* fix(reposcan): delete from new dependent tables ([`ebcb5cb`](https://github.com/RedHatInsights/vmaas/commit/ebcb5cb83f58dd0342c9c12dc8ce745e5829c0f0))

## v2.13.1 (2021-04-21)

### Fix

* fix(webapp): include packages without errata ([`4b4e409`](https://github.com/RedHatInsights/vmaas/commit/4b4e409769dd14864f8275f51118beda159fa4d8))

## v2.13.0 (2021-04-20)

### Chore

* chore: update to current manifest format ([`76bc06c`](https://github.com/RedHatInsights/vmaas/commit/76bc06cc81ed5bd7ab3784d425b1f2221e0d716a))

### Feature

* feat(webapp): add &#34;modified_since&#34; support to /pkgtree v3 ([`922c84b`](https://github.com/RedHatInsights/vmaas/commit/922c84bab2dc2af861f1d6cba362dc6dc58cc887))

## v2.12.0 (2021-04-20)

### Feature

* feat(webapp): add new /pkgtree endpoint options
- return_{errata, repositories, summary, description} ([`5811f2f`](https://github.com/RedHatInsights/vmaas/commit/5811f2f6da52c8fbf192ce01944b230bb3a1d2bb))

## v2.11.0 (2021-04-19)

### Chore

* chore: sync cached oval in gh actions ([`8798f23`](https://github.com/RedHatInsights/vmaas/commit/8798f23d73d9fb6b3c8a019c1b7be78015b1927c))

* chore: reposcan with env var in gh action ([`5997fed`](https://github.com/RedHatInsights/vmaas/commit/5997fed305e9998dbff4c6044816185865d6b38d))

* chore: fix docker run in ci.yml ([`fe8eb4e`](https://github.com/RedHatInsights/vmaas/commit/fe8eb4e4d0ab9c61c6df4efd487387b16e02f4f6))

### Feature

* feat(webapp): added summary and description info to /pkgtree response v3 ([`909d7c3`](https://github.com/RedHatInsights/vmaas/commit/909d7c36368e003c616f21acff8df34204928929))

### Unknown

* Updated pr check to use absolute paths

Signed-off-by: bennyturns &lt;bturner@redhat.com&gt; ([`ddeeb1f`](https://github.com/RedHatInsights/vmaas/commit/ddeeb1f52a73f9398775003d704de2b86e5c65f2))

## v2.10.0 (2021-04-16)

### Chore

* chore(webapp): cleaned pkgtree.py code ([`6229604`](https://github.com/RedHatInsights/vmaas/commit/6229604a6010550354305defd991b90b1afa57d1))

* chore: use iqe-vmaas-plugin ([`02956eb`](https://github.com/RedHatInsights/vmaas/commit/02956eb4facc89c257b4df8db9dd0abf7d9f66fc))

* chore: remove integration tests on osd3 ([`fec4f97`](https://github.com/RedHatInsights/vmaas/commit/fec4f9755c2d3c32b3d33b4a8d1f166efbe6ce6f))

* chore: set OVAL feed in clowdapp and gh actions ([`cdd59aa`](https://github.com/RedHatInsights/vmaas/commit/cdd59aae15db504f2392ecec091ac433bdcbefcc))

### Feature

* feat(webapp): added pagination to /pkgtree (api_version=3) ([`568497d`](https://github.com/RedHatInsights/vmaas/commit/568497df7f29fa139c0544a863c525a613110ba4))

## v2.9.0 (2021-04-15)

### Feature

* feat(reposcan): Add support for different git repolist branches ([`d7f8446`](https://github.com/RedHatInsights/vmaas/commit/d7f8446b35ad08ded908bd95d9e718ea1991b33a))

### Unknown

* feat(webapp) added input regex support to &#34;pkgtree&#34; endpoint ([`ab3bbe8`](https://github.com/RedHatInsights/vmaas/commit/ab3bbe8e25d26caefead02e75f376e50ac04e31b))

* chore(webapp) added common func. for input regex &#34;try_expand_by_regex&#34; ([`717583d`](https://github.com/RedHatInsights/vmaas/commit/717583d17693d8eaf4c32f527972fceec5aec307))

* Simpler pkgtree response in openapi docs ([`ffa7cc8`](https://github.com/RedHatInsights/vmaas/commit/ffa7cc848ad4996732eebffe9fe1e899a1668c43))

## v2.8.2 (2021-04-08)

### Chore

* chore: don&#39;t push qa image tag in build_deploy ([`154080f`](https://github.com/RedHatInsights/vmaas/commit/154080fca22685a1b10feb53939937d563313c9a))

### Fix

* fix(webapp): close dbm after loading cache ([`e6aad5c`](https://github.com/RedHatInsights/vmaas/commit/e6aad5c3f3e34527dd74ab347d5a272170d337b3))

## v2.8.1 (2021-04-08)

### Fix

* fix(reposcan): import CPEs even if not found in CPE dict ([`fba7ffb`](https://github.com/RedHatInsights/vmaas/commit/fba7ffb5e83ec89ce3d128cd5d40f3715e8df9da))

* fix(reposcan): empty insert ([`49022a4`](https://github.com/RedHatInsights/vmaas/commit/49022a415a964999b5ac45097f15c96d98be3990))

## v2.8.0 (2021-04-08)

### Feature

* feat(reposcan): support cleaning /tmp manually ([`504aa3d`](https://github.com/RedHatInsights/vmaas/commit/504aa3dd34839ee9b281b566c8f90ee711f80aef))

## v2.7.1 (2021-04-07)

### Chore

* chore: /rebase command for PRs ([`6597f3b`](https://github.com/RedHatInsights/vmaas/commit/6597f3b3e9e9db13b87fc45f0bf55fd4d1fedb7d))

### Fix

* fix(reposcan): handling of repolist urls ([`de3b8a0`](https://github.com/RedHatInsights/vmaas/commit/de3b8a0595bb5d0ff95d63258100ba47ab4a5445))

## v2.7.0 (2021-04-06)

### Feature

* feat(webapp): Third party content support - Webapp

Signed-off-by: mhornick &lt;mhornick@redhat.com&gt; ([`c001a8d`](https://github.com/RedHatInsights/vmaas/commit/c001a8db08efde47786ddcd119adf314288b5fea))

## v2.6.0 (2021-04-06)

### Chore

* chore: refactor and mirror health endpoint for clowder ([`30aa9ad`](https://github.com/RedHatInsights/vmaas/commit/30aa9ad17ae09f2e4d022f2c1c99501ed620d7d8))

### Feature

* feat(reposcan): parse and store OVAL data ([`c66d0e4`](https://github.com/RedHatInsights/vmaas/commit/c66d0e46931148a9dd57a14819b6d60f8d3be0b9))

* feat(reposcan): download OVAL files to tmp dir and unpack ([`737c0f3`](https://github.com/RedHatInsights/vmaas/commit/737c0f33baf748e2ee84561eeba5cadd26ec72b6))

* feat(reposcan): register sync API for OVAL files ([`9673f42`](https://github.com/RedHatInsights/vmaas/commit/9673f4224f06a1cd78a007f941a32cea113d4407))

### Unknown

* cleaned new methods in updates.py ([`70856e4`](https://github.com/RedHatInsights/vmaas/commit/70856e4d023eb4055a3e2236bb3e1870aed5c5d4))

* implemented &#34;webapp.updates._get_optimistic_updates&#34; (by mim) ([`e398389`](https://github.com/RedHatInsights/vmaas/commit/e39838930e055b2a202289fafaf20282cb157fee))

* added test and mock implementation for &#34;optimistic_updates&#34; ([`d5eec9f`](https://github.com/RedHatInsights/vmaas/commit/d5eec9f575ffe33dd76fa9eb8f8e60571baf6fe3))

* updated webapp API with &#34;optimistic_updates&#34; flag ([`3c123de`](https://github.com/RedHatInsights/vmaas/commit/3c123def9de8fc10318b0d36f05e514f577e07d0))

## v2.5.0 (2021-03-29)

### Feature

* feat(reposcan): Third-party content support, reposcan ([`7d203aa`](https://github.com/RedHatInsights/vmaas/commit/7d203aa6beb56a68d9e2338615472a89548e3e94))

### Unknown

* add third_party flag to API spec ([`385541b`](https://github.com/RedHatInsights/vmaas/commit/385541ba08c681c275dcd7ce546861eba72ffc62))

## v2.4.1 (2021-03-26)

### Fix

* fix(webapp): fixed asserts in test_updates.py

modified the input to get some real updates ([`f31e3dc`](https://github.com/RedHatInsights/vmaas/commit/f31e3dc3047a8a5d0edabbc4d32bdb9c1ad5332d))

### Unknown

* refactored updates.py to be easier to read ([`bc2dbe6`](https://github.com/RedHatInsights/vmaas/commit/bc2dbe6869012d8d8daa09bcbf2d5f1517b00702))

## v2.4.0 (2021-03-23)

### Chore

* chore: update aiohttp to fix CVE-2021-21330 ([`e110a63`](https://github.com/RedHatInsights/vmaas/commit/e110a63849cda0d08196ecd6472eb614fc4b7a5d))

### Feature

* feat(webapp): define interface for patched/unpatched CVEs and OVAL evaluation toggles ([`125c839`](https://github.com/RedHatInsights/vmaas/commit/125c8397041c138b09c611d19095258151321aae))

## v2.3.0 (2021-03-18)

### Chore

* chore(reposcan): remove unused variable ([`6b48270`](https://github.com/RedHatInsights/vmaas/commit/6b482700d48518b51763647d6163e6bc62ec923e))

* chore: add GH releases badge ([`c3e8f8c`](https://github.com/RedHatInsights/vmaas/commit/c3e8f8c394d69a4150bab8ecae2637afc67d0e4e))

* chore: change Travis badge to GH Actions ([`3398072`](https://github.com/RedHatInsights/vmaas/commit/3398072effd0f15daf489cd7d44fc18a0a893dc2))

* chore: use turnpike to sync repolist ([`52f856f`](https://github.com/RedHatInsights/vmaas/commit/52f856fa56ac4bd73c573f2171793f0c92090cfc))

### Feature

* feat(webapp): show CPEs in /repos API ([`e080845`](https://github.com/RedHatInsights/vmaas/commit/e080845f5a3523f851dea20711fabd4a5f16ad0e))

* feat(reposcan): export imported CPE metadata ([`c1e441b`](https://github.com/RedHatInsights/vmaas/commit/c1e441bed7cc4e73c47fe203da7790d3c6545cc2))

* feat(reposcan): sync CPE metadata into DB ([`b688f9f`](https://github.com/RedHatInsights/vmaas/commit/b688f9f8eeee1d766a3b41c1e6c45978c6fd22f9))

* feat(database): introduce cpe tables ([`8247fde`](https://github.com/RedHatInsights/vmaas/commit/8247fded0468b7f19846b8d3827cdc13c1935bba))

## v2.2.1 (2021-03-08)

### Fix

* fix: waiting for DB and rsync port in e2e-deploy and docker-compose ([`9aad355`](https://github.com/RedHatInsights/vmaas/commit/9aad35511be74ef0dfa74ca5b8c8a829b08da3db))

## v2.2.0 (2021-03-05)

### Feature

* feat(clowder): integrate with clowder ([`e419895`](https://github.com/RedHatInsights/vmaas/commit/e419895249391f3a6c00f363435f97084ae2b215))

## v2.1.1 (2021-03-03)

### Chore

* chore(gh_action): correct path, install tar ([`a5a8582`](https://github.com/RedHatInsights/vmaas/commit/a5a8582d6dbfb87665876d3b5c6ff1d6e5f185ea))

* chore: use redhat-actions/oc-installer ([`e416841`](https://github.com/RedHatInsights/vmaas/commit/e416841ee4cef85a619578c0c2a0df84c837ad33))

* chore: there is no fix for tornado vulnerability yet, disable this one check

39462: tornado &lt;=6.1 resolved (6.0.3 installed)!
All versions of package tornado are vulnerable to Web Cache Poisoning by using a vector called parameter cloaking. When the attacker can separate query parameters using a semicolon (;), they can cause a difference in the interpretation of the request between the proxy (running with default configuration) and the server. This can result in malicious requests being cached as completely safe ones, as the proxy would usually not see the semicolon as a separator, and therefore would not include it in a cache key of an unkeyed parameter. See CVE-2020-28476. ([`fe4ec5f`](https://github.com/RedHatInsights/vmaas/commit/fe4ec5ff99935b42b44509a164df4b800e8e5198))

### Fix

* fix(reposcan): replace github auth with turnpike

no complete authentication/authorization done here, we just parse&amp;log header from turnpike ([`d0e5a4f`](https://github.com/RedHatInsights/vmaas/commit/d0e5a4f639fd00f9a9a5c12238ab1bb734526d87))

## v2.1.0 (2021-01-28)

### Chore

* chore: standardize API versioning (v2/v3 available for all endpoints) and prepare new base path for 3scale ([`8563363`](https://github.com/RedHatInsights/vmaas/commit/856336392b2ad9b33d7c474ab59cbb3e5e2d46b0))

* chore: bump vmaas major version ([`245aee5`](https://github.com/RedHatInsights/vmaas/commit/245aee5ec64cbb8283763f0187bcf8a88815994f))

* chore: update libs ([`ea5d3e2`](https://github.com/RedHatInsights/vmaas/commit/ea5d3e2b2c8d5c6b252f7eb9b9aba36e224f069d))

## v1.20.7 (2021-01-05)

### Fix

* fix(webapp): check if websocket is open before message is sent and ensure concurrency

VMAAS-1315

asyncio: [ERROR] Task exception was never retrievedfuture: &lt;Task finished coro=&lt;Websocket._refresh_cache() done, defined at /vmaas/webapp/app.py:422&gt; exception=AttributeError(&#34;&#39;NoneType&#39; object has no attribute &#39;send_str&#39;&#34;,)&gt;&#39;Traceback (most recent call last):\n  File &#34;/vmaas/webapp/app.py&#34;, line 428, in _refresh_cache\n    await self.report_version()\n  File &#34;/vmaas/webapp/app.py&#34;, line 476, in report_version\n    await self.websocket.send_str(f&#34;version {BaseHandler.db_cache.dbchange.get(\&#39;exported\&#39;)}&#34;)\nAttributeError: \&#39;NoneType\&#39; object has no attribute \&#39;send_str\&#39;&#39;| ([`6f529d1`](https://github.com/RedHatInsights/vmaas/commit/6f529d1a014441c7341bd89f32bc32fde728685f))

## v1.20.6 (2020-12-03)

### Fix

* fix(reposcan): skip repos with invalid sqlite database ([`35388b5`](https://github.com/RedHatInsights/vmaas/commit/35388b551c3de19f745f50451601e898c3b09b7b))

## v1.20.5 (2020-11-19)

### Chore

* chore: replace Travis CI with Github Actions ([`c7843c1`](https://github.com/RedHatInsights/vmaas/commit/c7843c1148b1e6a66563830096965017f254f4e0))

* chore: update all dependencies

This reverts commit d2795913d105b1ebcfceda913f0d197b5768bb7d. ([`736fdfa`](https://github.com/RedHatInsights/vmaas/commit/736fdfa32e0e96e80baae0c4008823b71f0d809b))

* chore: re-lock dependencies ([`d279591`](https://github.com/RedHatInsights/vmaas/commit/d2795913d105b1ebcfceda913f0d197b5768bb7d))

### Fix

* fix: duplicate messages in kibana ([`a296cb9`](https://github.com/RedHatInsights/vmaas/commit/a296cb97cc6b2c4ad344f323ddbc3835963a9b01))

### Test

* test: caret is now escaped in the response ([`a50f854`](https://github.com/RedHatInsights/vmaas/commit/a50f85455ab3e0b824cad70b80136b37c6c25fc9))

### Unknown

* Revert &#34;test: caret is now escaped in the response&#34;

This reverts commit a50f85455ab3e0b824cad70b80136b37c6c25fc9. ([`c71596f`](https://github.com/RedHatInsights/vmaas/commit/c71596f7b33db9d1e4ca75e7354419205845cdf7))

## v1.20.4 (2020-10-29)

### Chore

* chore: grafana in stage/prod was updated ([`e27d81d`](https://github.com/RedHatInsights/vmaas/commit/e27d81d9251217cd23174466fce8961ef8142da3))

* chore: update RDS metrics ([`3f8f561`](https://github.com/RedHatInsights/vmaas/commit/3f8f561c2ed94550ec54d3f7fa7f66d46a2397fe))

### Fix

* fix: use pod name for log-stream in CW config ([`f03fed4`](https://github.com/RedHatInsights/vmaas/commit/f03fed4ff38fa50a6c1f414618759b724f8e3fc2))

## v1.20.3 (2020-10-09)

### Chore

* chore: integration tests openshift app entrypoint ([`9f49eab`](https://github.com/RedHatInsights/vmaas/commit/9f49eab11f143f52d84786e3b3fbf1af9a98cce7))

* chore: use different uid for vmaas ([`5553385`](https://github.com/RedHatInsights/vmaas/commit/55533851c5d95045394b95961c2197f1b53b9d9a))

* chore: create new grafana dashboard and fix local container ([`fdc8339`](https://github.com/RedHatInsights/vmaas/commit/fdc833996eded7455541f39888e38dd96c84e26b))

* chore: set to debug, it&#39;s overly verbose for some repos ([`4b351c5`](https://github.com/RedHatInsights/vmaas/commit/4b351c59981e49d6844a04e9d73147fc95ed608b))

* chore: coverage binary name in ubi ([`ca89b60`](https://github.com/RedHatInsights/vmaas/commit/ca89b6070ffd8bb1557ffde298bd75eab3902573))

* chore: add python3-coverage to qe build ([`3809d9b`](https://github.com/RedHatInsights/vmaas/commit/3809d9b725a943673d68fe1e722c245d8f3ead14))

### Fix

* fix(reposcan): detect case when sync process is killed and reposcan is stucked ([`b0797e8`](https://github.com/RedHatInsights/vmaas/commit/b0797e81b9d03cf54b647c02c4db188f7145006f))

## v1.20.2 (2020-09-23)

### Chore

* chore: improve logging settings ([`cdd6002`](https://github.com/RedHatInsights/vmaas/commit/cdd60025317d76e67c300690a6b48b10a8bc0090))

### Fix

* fix(webapp): init logging once ([`dcbaff3`](https://github.com/RedHatInsights/vmaas/commit/dcbaff349b57c9b711c3a0b73130c39708e5fde8))

## v1.20.1 (2020-09-22)

### Fix

* fix(webapp): only format error if response has body ([`07c60d0`](https://github.com/RedHatInsights/vmaas/commit/07c60d09a7aed0f7409ace5b486909346b71ec67))

### Unknown

* Use marker for vmaas tests ([`7320c46`](https://github.com/RedHatInsights/vmaas/commit/7320c46d11d9d53347cf3afb5ff5cd21bd1a0a9c))

## v1.20.0 (2020-09-21)

### Feature

* feat(webapp): install rpm module ([`675c4e6`](https://github.com/RedHatInsights/vmaas/commit/675c4e67c1786f7074b33a1ab33f22c4032b3553))

* feat(webapp): update /updates to support latest_only filtering ([`e1fe2af`](https://github.com/RedHatInsights/vmaas/commit/e1fe2afa441f2d857410c318ae91bfebb938b953))

* feat(webapp): added function to filter latest NEVRAs ([`f1a662c`](https://github.com/RedHatInsights/vmaas/commit/f1a662ce2215006c1b09e0c07c2d28cc846b897a))

### Fix

* fix(webapp): if there is no dump, websocket handler crashes due to KeyError ([`25ae1f5`](https://github.com/RedHatInsights/vmaas/commit/25ae1f55985ec32907c656ea5f6e9caf4518489f))

* fix(common): updated tests for rpm.parser_rpm_name ([`9c505bf`](https://github.com/RedHatInsights/vmaas/commit/9c505bf2fd4bb0c49e1a575fb1f359ebf5d614dc))

* fix: let pipenv see system site-packages ([`d5406ae`](https://github.com/RedHatInsights/vmaas/commit/d5406ae15def6b1194f3adca74563a2111dd14e3))

* fix: use new single app image ([`cb83321`](https://github.com/RedHatInsights/vmaas/commit/cb8332167b79f4accc87eed866b2a4ad74c4ad86))

* fix(reposcan): move function proper rpm module and reuse it ([`ba0124b`](https://github.com/RedHatInsights/vmaas/commit/ba0124b735bcd00446132694b4181792a24e0e7e))

* fix(webapp): reuse function from common.rpm ([`9c3b2fa`](https://github.com/RedHatInsights/vmaas/commit/9c3b2faae773a379b191dd523dbc08abcad8cdb2))

## v1.19.2 (2020-09-14)

### Fix

* fix(webapp): expose readiness endpoint ([`878d2c4`](https://github.com/RedHatInsights/vmaas/commit/878d2c4b3d3a07a74534dddafa806cd7bd054eb3))

## v1.19.1 (2020-09-12)

### Chore

* chore: fix new pylint 2.6.0 issues ([`9500390`](https://github.com/RedHatInsights/vmaas/commit/9500390cdd9efac866ea217d18b0945a20e30163))

* chore: podman-compose from devel branch doesn&#39;t have stable checksum, drop it from dependencies ([`3ae38d8`](https://github.com/RedHatInsights/vmaas/commit/3ae38d8821e01b55a4cbc09a5047fac4049c6047))

### Fix

* fix(webapp): don&#39;t block websocket during refresh ([`343044e`](https://github.com/RedHatInsights/vmaas/commit/343044ee957575ad62ad866a1e9ec59b3522813b))

* fix(websocket): track ids of clients in log ([`1b169fc`](https://github.com/RedHatInsights/vmaas/commit/1b169fcdbe8afc259cbc44cb6eecfe9f3366e0ed))

* fix(websocket): Progressively refresh webapps

	Add readiness endpoint to webapp

	Remove buffering queues from websocket implementations, make them steady-state ([`7f79ed4`](https://github.com/RedHatInsights/vmaas/commit/7f79ed4fb930a188e1403eda80d370c40d48bd24))

* fix: update developer mode to new single container ([`dd74dfa`](https://github.com/RedHatInsights/vmaas/commit/dd74dfab1e6b0f9a53661e4ccef05f07a1c6a90b))

### Unknown

* Merge pull request #749 from jdobes/gracefuly_exit_sleep

fix: gracefully exit sleeping scripts ([`08eeb41`](https://github.com/RedHatInsights/vmaas/commit/08eeb416f73ce3e329556315740298e25b5a2597))

## v1.19.0 (2020-09-02)

### Chore

* chore: added deps for cloudwatch logging ([`edfc83b`](https://github.com/RedHatInsights/vmaas/commit/edfc83b2bb5a8a033612889c5816b7b74ab828fe))

### Feature

* feat: added cloudwatch logging setup ([`2bf4c2d`](https://github.com/RedHatInsights/vmaas/commit/2bf4c2def3a29cd5304bb8698508fa6bec813ff6))

### Fix

* fix: build app image only once ([`a33dfdd`](https://github.com/RedHatInsights/vmaas/commit/a33dfddfde0da025cc4eb5d7427a13014e78e213))

## v1.18.3 (2020-07-29)

### Chore

* chore: update vmaas qe build on openshift ([`d1eac98`](https://github.com/RedHatInsights/vmaas/commit/d1eac98c2f0f596eedd6e7ecf80e57e4f2082188))

### Fix

* fix(reposcan): file content is required by crypto lib, not file name, also fixing detection for certs expiring in more than 30 days ([`11917f3`](https://github.com/RedHatInsights/vmaas/commit/11917f31e620f911f07be3745f882b716c93bca2))

* fix(reposcan): fixing ISE in prepare msg function

reposcan: [ERROR] Internal server error &lt;-9223363273888645507&gt;&#39;Traceback (most recent call last):\n  File &#34;/vmaas/reposcan/repodata/repository_controller.py&#34;, line 81, in _check_cert_expiration_date\n    loaded_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)\n  File &#34;/usr/local/lib/python3.6/site-packages/OpenSSL/crypto.py&#34;, line 1794, in load_certificate\n    _raise_current_error()\n  File &#34;/usr/local/lib/python3.6/site-packages/OpenSSL/_util.py&#34;, line 54, in exception_from_error_queue\n    raise exception_type(errors)\nOpenSSL.crypto.Error: [(\&#39;PEM routines\&#39;, \&#39;get_name\&#39;, \&#39;no start line\&#39;)]\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File &#34;/vmaas/reposcan/reposcan.py&#34;, line 518, in run_task\n    repository_controller.store()\n  File &#34;/vmaas/reposcan/repodata/repository_controller.py&#34;, line 272, in store\n    failed = self._download_repomds()\n  File &#34;/vmaas/reposcan/repodata/repository_controller.py&#34;, line 72, in _download_repomds\n    self._check_cert_expiration_date(cert_name, cert)\n  File &#34;/vmaas/reposcan/repodata/repository_controller.py&#34;, line 96, in _check_cert_expiration_date\n    msg = prepare_msg_for_slack(cert_name, \&#39;Reposcan CDN certificate not provided or incorrect\&#39;)\n  File &#34;/vmaas/reposcan/common/slack_notifications.py&#34;, line 48, in prepare_msg_for_slack\n    (valid_to_dt, expire_in_days_td) = expire_tuple\nTypeError: \&#39;NoneType\&#39; object is not iterable&#39;| ([`04c7258`](https://github.com/RedHatInsights/vmaas/commit/04c7258dfc630172ace90e73ad7ee8cfbe9c0104))

## v1.18.2 (2020-07-23)

### Documentation

* docs: specify possible values in schema

Removed basearch enum

Removed commented code

Finished updating specs.

Moved null to end ([`75a6de7`](https://github.com/RedHatInsights/vmaas/commit/75a6de7575b37f345ab2517343535ee56cf33060))

### Fix

* fix: fix path to wait script ([`d0fcdc1`](https://github.com/RedHatInsights/vmaas/commit/d0fcdc103970cdcdda68e781bc902fa4541209ce))

### Refactor

* refactor: use single dockerfile for all app services ([`aa21829`](https://github.com/RedHatInsights/vmaas/commit/aa21829807ced2b2339834972e2dd52f92a19497))

## v1.18.1 (2020-07-10)

### Fix

* fix(reposcan): export pkg_cve mappings only for cves with source ([`3bb9bac`](https://github.com/RedHatInsights/vmaas/commit/3bb9bacc56b6502f6f11aa5e88f1bba11ed5f564))

## v1.18.0 (2020-07-09)

### Feature

* feat(reposcan): add cdn expiration notifications to slack ([`25e61f4`](https://github.com/RedHatInsights/vmaas/commit/25e61f400538b5f4ead453af74422ae82c658b51))

## v1.17.4 (2020-07-08)

### Fix

* fix(websocket): fix key error and incorrect timestamp extraction ([`3c0e4c0`](https://github.com/RedHatInsights/vmaas/commit/3c0e4c0815deaff3fa0c359fd88878dab54b56f7))

## v1.17.3 (2020-07-02)

### Fix

* fix(webapp): added non module testing update into the webapp tests ([`3041854`](https://github.com/RedHatInsights/vmaas/commit/30418541e9f403a6d5028534cf8a35ac2b28f95b))

* fix(webapp): updated tests default modules update ([`ad063ef`](https://github.com/RedHatInsights/vmaas/commit/ad063ef46647596ef6e9936ea9d8e28cc356e3cd))

* fix(webapp): removed updates when modules_list is not provided ([`952a89c`](https://github.com/RedHatInsights/vmaas/commit/952a89cdaa5a907cd753bbe009aefa26fe64b22e))

## v1.17.2 (2020-06-25)

### Fix

* fix(webapp): fixed webapp response gzipping ([`29d7988`](https://github.com/RedHatInsights/vmaas/commit/29d798845dc0bfcdb1898cdd6dc4d43f85b13644))

### Unknown

* Reduce times for websocket ([`1496e56`](https://github.com/RedHatInsights/vmaas/commit/1496e5675b497521872911e5aef4750fcab17f52))

* fixed errata saving, removed severity key error ([`04f8be9`](https://github.com/RedHatInsights/vmaas/commit/04f8be9321bb937730b5ca24b42ff89b152eaa0f))

## v1.17.1 (2020-06-24)

### Fix

* fix(reposcan): delete rows from module_rpm_artifact ([`f8889a4`](https://github.com/RedHatInsights/vmaas/commit/f8889a4fc3449bdc29187518e0d500f83948f8c0))

* fix(reposcan): add src_pkg_names to content set mapping to cache ([`c7020e7`](https://github.com/RedHatInsights/vmaas/commit/c7020e701616a2adcef033bc5a5cb6f1b39803de))

## v1.17.0 (2020-06-19)

### Feature

* feat(webapp): unify errata severity none to null ([`f2cddad`](https://github.com/RedHatInsights/vmaas/commit/f2cddad847ffdd6a9577a295945cb4f058cfc232))

### Fix

* fix(reposcan): fix bugs in db tests ([`4156bfb`](https://github.com/RedHatInsights/vmaas/commit/4156bfbcceea1b12d7756aa76413e3556905c0ed))

### Unknown

* fixed gzipping swagger responses in webapp ([`6181b10`](https://github.com/RedHatInsights/vmaas/commit/6181b10572968efdfa022699668dc582dbdbdbb4))

## v1.16.1 (2020-06-16)

### Fix

* fix(reposcan): close DB connection when background tasks finishes ([`4d0d3a8`](https://github.com/RedHatInsights/vmaas/commit/4d0d3a84903f5eb91119443cfe066249b7a20a19))

### Refactor

* refactor: tag experimental endpoints ([`51b97fa`](https://github.com/RedHatInsights/vmaas/commit/51b97fab0b3d13f085b1a80e098b7e12ca341fbf))

## v1.16.0 (2020-06-11)

### Feature

* feat(webapp): return only those CVEs which have errata associated ([`c602508`](https://github.com/RedHatInsights/vmaas/commit/c602508179ec9083a86718d3c5e3379cbc1e05ff))

### Refactor

* refactor: remove version lock workaround ([`75f702b`](https://github.com/RedHatInsights/vmaas/commit/75f702bf9a83f440ed60ccbecd33c9eb8ca47179))

## v1.15.2 (2020-06-05)

### Fix

* fix(webapp): removed redundant product check

including updates from different repos of the same product
confuses users because they see updates from repos which they do not
have enabled ([`1a8a5ba`](https://github.com/RedHatInsights/vmaas/commit/1a8a5ba355ab314143653a7d8e8eb421c3de7a59))

### Refactor

* refactor(database): initialize schema if database container is not present (RDS) ([`9be7e4c`](https://github.com/RedHatInsights/vmaas/commit/9be7e4cd3b3d0ce22599851800385951a2735062))

### Test

* test: install gcc, python3-devel due to psutil build and remove ubi8 version lock ([`664cf1f`](https://github.com/RedHatInsights/vmaas/commit/664cf1ffd68317f399ee96b18c3d7d958a9c6eef))

### Unknown

* Remove debug code from srpm API code ([`ea90892`](https://github.com/RedHatInsights/vmaas/commit/ea908925fb523d1c99f6852acee55e9458e3fc00))

* Fix srpm API performance that resulted in timeouts ([`d207be2`](https://github.com/RedHatInsights/vmaas/commit/d207be2ca8e582f38d47afad61b05048c64c2139))

## v1.15.1 (2020-05-26)

### Fix

* fix(webapp): fixed gzip middleware null-pointer ([`134fcf8`](https://github.com/RedHatInsights/vmaas/commit/134fcf8da5ed598701416ceb59b6ebd5f41ad5d8))

## v1.15.0 (2020-05-22)

### Feature

* feat(common): add slack notification module ([`3664752`](https://github.com/RedHatInsights/vmaas/commit/3664752de9429d7e2c9f0c0d2aaef8b830f06014))

## v1.14.1 (2020-05-20)

### Fix

* fix(reposcan): export package names without errata ([`05fe569`](https://github.com/RedHatInsights/vmaas/commit/05fe569a6377a6a0defbc17f81f45217b85cefb0))

### Test

* test: make upgrade test work in dirty git in container ([`5acb7ec`](https://github.com/RedHatInsights/vmaas/commit/5acb7ec67cfbbf51b503ef58ef1f93386856ace6))

## v1.14.0 (2020-05-18)

### Chore

* chore: pipenv check workaround

https://github.com/pypa/pipenv/issues/4188

PIPENV_PYUP_API_KEY= can be removed when pipenv-2020.X.X is released ([`5c6ac7d`](https://github.com/RedHatInsights/vmaas/commit/5c6ac7d613c05355d1d4f4f3c5af6d8a9891dce2))

### Feature

* feat(webapp): add errata filtering by severity and errata type ([`b0b4df5`](https://github.com/RedHatInsights/vmaas/commit/b0b4df5308779551a9b3abd83e44e81b18972279))

### Unknown

* added gzip response middleware ([`327c588`](https://github.com/RedHatInsights/vmaas/commit/327c58843c1b8edcd2438afa60142075369558e1))

## v1.13.5 (2020-05-05)

### Fix

* fix(webapp): fix content set filtering in package_names/srpms api endpoint ([`ee323bf`](https://github.com/RedHatInsights/vmaas/commit/ee323bfc0da8ad80efffe8c936d80f488f862214))

## v1.13.4 (2020-05-05)

### Chore

* chore: re-lock dependencies to update pylint

Pylint 2.5.0 no longer allows python -m pylint ... to import user code. Previously, it added the current working directory as the first element of sys.path. This opened up a potential security hole where pylint would import user level code as long as that code resided in modules having the same name as stdlib or pylint&#39;s own modules. ([`6226541`](https://github.com/RedHatInsights/vmaas/commit/6226541e10a65fd145acdf3e0c2c0e7958f309fd))

* chore: fix collecting openshift logs in actions ([`b32c0da`](https://github.com/RedHatInsights/vmaas/commit/b32c0da151f9f58b5d0430524d0d111dfcb03ded))

* chore: deploy to openshift ([`360cf5e`](https://github.com/RedHatInsights/vmaas/commit/360cf5ef3501503beb805daa1d95613493c27fe2))

### Fix

* fix(webapp): remove unused argument and imports ([`5a695d7`](https://github.com/RedHatInsights/vmaas/commit/5a695d72561f1899c1538caae50efc2246bfd6eb))

* fix(webapp): removed hotcache

according to performance testing and the production monitoring the hit/miss ratio
of the hotcache is so low that it&#39;s actually slowing evaluation ([`68e7528`](https://github.com/RedHatInsights/vmaas/commit/68e75287205d5107a6393d7995e56f872ad40dbc))

### Test

* test: fix pylint 2.5.0 issues ([`f90dcb6`](https://github.com/RedHatInsights/vmaas/commit/f90dcb660864fed852436e16a7b90c46794a7e2e))

### Unknown

* fix(webapp) removed hotcache tests ([`0b00e44`](https://github.com/RedHatInsights/vmaas/commit/0b00e446a61d4883da1c1e45b2d617f654d8f1dc))

## v1.13.3 (2020-04-27)

### Chore

* chore: fix upgrade test to find old commit ([`d1a217b`](https://github.com/RedHatInsights/vmaas/commit/d1a217b710b51202ad5bbc3dee6e45593b07cc97))

### Fix

* fix(webapp): distinguish existining and nonex. packages on /rpms ([`e417401`](https://github.com/RedHatInsights/vmaas/commit/e4174019434d0b00a2d6c8be30c80771ae8c2036))

* fix(webapp): distinguish existining and nonex. packages on /srpms ([`d7f4e50`](https://github.com/RedHatInsights/vmaas/commit/d7f4e500a320cc6916c196ed4bd9b88097b82f40))

## v1.13.2 (2020-04-22)

### Fix

* fix(reposcan): Do not show bad token to log ([`c4f1c0d`](https://github.com/RedHatInsights/vmaas/commit/c4f1c0d36556860ffd40250f18a1f3cc7db1208a))

## v1.13.1 (2020-04-20)

### Fix

* fix: patches API should return ALL errata, not just security ones ([`82f80a8`](https://github.com/RedHatInsights/vmaas/commit/82f80a87c136791643ef6285e900bc2455bb3fc4))

## v1.13.0 (2020-04-20)

### Feature

* feat(webapp): add new POST and GET /package_names/rpms API endpoint ([`a64aa2e`](https://github.com/RedHatInsights/vmaas/commit/a64aa2e8b5b6fcb63a815387baec1724571cfa15))

* feat(webapp): add /package_names api endpoint

test(package_names): add unit tests for package_names

feat(webapp): move from /package_names to /package_names/srpms and separate srpms and rpms calls and add GET method to /srpms ([`bda5cb5`](https://github.com/RedHatInsights/vmaas/commit/bda5cb5ef880b7a697c67ccf6d56870f2d64f9ca))

## v1.12.2 (2020-04-17)

### Chore

* chore: Fix command in devel docker composes for podman-compose ([`2d10aef`](https://github.com/RedHatInsights/vmaas/commit/2d10aefca114359b142b751202ad5fc86617a7ed))

* chore: disable PIPENV_CHECK in actions run ([`6bcccf9`](https://github.com/RedHatInsights/vmaas/commit/6bcccf952542bf0a60573fcdba7e2e28f113dee1))

* chore: run actions only on pushes to master+stable and on PRs to stable (coming from branch on same repo to make it work) ([`336f062`](https://github.com/RedHatInsights/vmaas/commit/336f06268487ef2ae29ef1a92e7dd7a30551609f))

### Fix

* fix: there may not be any dump loaded ([`4fbb326`](https://github.com/RedHatInsights/vmaas/commit/4fbb3268f7ccc5077281b093dd5303e7c983fde0))

* fix(database): default 64mb is not always enough for PostgreSQL 12 ([`0677cab`](https://github.com/RedHatInsights/vmaas/commit/0677cab792eec7e4928251055f96ebcf04616ee4))

## v1.12.1 (2020-04-16)

### Chore

* chore: allow to get PIPENV_CHECK variable from host environment

allows commands like:
$ PIPENV_CHECK=0 docker-compose up --build ([`89c0e08`](https://github.com/RedHatInsights/vmaas/commit/89c0e08fdccb68f4c2bfe13a8b8294dc1366e84d))

### Fix

* fix(webapp): switch to refreshing mode and return 503 ([`f5e15ab`](https://github.com/RedHatInsights/vmaas/commit/f5e15ab4a52f81d1b4d4ef3510c7d7773d7f1516))

* fix(webapp): don&#39;t block API during cache refreshes ([`9b85909`](https://github.com/RedHatInsights/vmaas/commit/9b8590991853d94f4b40e75967624f6a861ced01))

## v1.12.0 (2020-04-15)

### Chore

* chore: pass PIPENV_CHECK variable to test build from travis env ([`1711814`](https://github.com/RedHatInsights/vmaas/commit/1711814bb6630d16182bd08015252cd9ea315d22))

* chore: fix missing /common in developer setup ([`670040a`](https://github.com/RedHatInsights/vmaas/commit/670040aae51da85358b2fceea3ac651eb8c533a0))

* chore: make an easy way to disable pipenv check when necessary ([`24f269b`](https://github.com/RedHatInsights/vmaas/commit/24f269b862d42edfef4b849488e1a37902987c55))

* chore: fix podman devel setup ([`665bf0b`](https://github.com/RedHatInsights/vmaas/commit/665bf0b2bf17c1b7c8c12b4bc25fffef9ec2c1dd))

### Feature

* feat(webapp): new API to list only applicable errata to a package list ([`8c92679`](https://github.com/RedHatInsights/vmaas/commit/8c9267983ccc1f6a61a7575b4148be6f8a159dfe))

## v1.11.3 (2020-04-09)

### Chore

* chore: remove obsoleted deployment scripts ([`89b390e`](https://github.com/RedHatInsights/vmaas/commit/89b390e27a540574808ac17d25414f048f9c364f))

* chore: use secrets project for vmaas secrets in jenkins ([`77e9fbd`](https://github.com/RedHatInsights/vmaas/commit/77e9fbd855fd2a42ebe6d4d8f22a9c5a8cdf9359))

### Fix

* fix(reposcan): 8.1-409 has broken dependencies in UBI repo

error: Error running transaction: package systemd-libs-239-18.el8_1.5.x86_64 (which is newer than systemd-libs-239-18.el8_1.4.x86_64) is already installed ([`edfee79`](https://github.com/RedHatInsights/vmaas/commit/edfee7945f61d40565ea1dcf9504c38f4e3508bd))

## v1.11.2 (2020-03-31)

### Fix

* fix(webapp): fix cache data race fetching when websocket crashes ([`d9c9ae8`](https://github.com/RedHatInsights/vmaas/commit/d9c9ae8acee1ada883e3cb4e7dc0cc3c5a1d28e5))

* fix(webapp): add webapp automatical reconnect to ws ([`403e209`](https://github.com/RedHatInsights/vmaas/commit/403e209ff5a9d7dcd7d58ce1a005c1dab2a9d902))

## v1.11.1 (2020-03-27)

### Fix

* fix(reposcan): PG 12 to_timestamp() behaviour changed

PG 10:
select to_timestamp(&#39;2020-03-26 19:38:26.195650+00:00&#39;, &#39;YYYY-MM-DD HH24:MI:SS.US&#39;); PASS
select to_timestamp(&#39;2020-03-26T19:37:00.846691+00:00&#39;, &#39;YYYY-MM-DD HH24:MI:SS.US&#39;); PASS

but PG 12:
select to_timestamp(&#39;2020-03-26 19:38:26.195650+00:00&#39;, &#39;YYYY-MM-DD HH24:MI:SS.US&#39;); PASS
select to_timestamp(&#39;2020-03-26T19:37:00.846691+00:00&#39;, &#39;YYYY-MM-DD HH24:MI:SS.US&#39;); FAIL

this works:
select to_timestamp(&#39;2020-03-26 19:38:26.195650+00:00&#39;, &#39;YYYY-MM-DDTHH24:MI:SS.US&#39;); PASS
select to_timestamp(&#39;2020-03-26T19:37:00.846691+00:00&#39;, &#39;YYYY-MM-DDTHH24:MI:SS.US&#39;); PASS ([`1a05925`](https://github.com/RedHatInsights/vmaas/commit/1a05925f032c48323f0be3b5b2a1e82838b89350))

* fix: &#39;pipenv install&#39; re-generates lockfile by default, install only from what&#39;s already in lockfile ([`3fde6d4`](https://github.com/RedHatInsights/vmaas/commit/3fde6d4fc8a1a4008f9bb4914f007cbfdc0cc772))

* fix: update pyyaml (CVE-2020-1747) and some others to fix tests ([`24a6890`](https://github.com/RedHatInsights/vmaas/commit/24a68904f23ada927bc1687aff11630bc664d5e9))

* fix(reposcan): duplicate error when import repos ([`29d275e`](https://github.com/RedHatInsights/vmaas/commit/29d275e96b6cc684c048112dfa7e8bff86c4efd7))

### Test

* test: workaround using UnsafeLoader in tests ([`8ed26bd`](https://github.com/RedHatInsights/vmaas/commit/8ed26bdb9c927f9e6750a644b7e133d5511ee453))

* test: base test image on UBI 8 and PG 12 ([`43d9985`](https://github.com/RedHatInsights/vmaas/commit/43d99854d44b78e7006f93abf3dad59a4d2440ad))

## v1.11.0 (2020-03-25)

### Feature

* feat(database): upgrade to PostgreSQL 12

re-introduce 2 dockerfiles because registry.redhat.io doesn&#39;t allow unauthenticated download ([`b6c61a9`](https://github.com/RedHatInsights/vmaas/commit/b6c61a9b25075135f0f7a461c5c3b8c3dee9b904))

### Fix

* fix(reposcan): install postgresql for DB migrations

- not available from UBI repos
- microdnf install from custom repo fails in OpenShift env, using workaround using rpm ([`e8b6210`](https://github.com/RedHatInsights/vmaas/commit/e8b621092b5ffd2e282ebc44c25c29e4fc6fbf19))

## v1.10.3 (2020-03-24)

### Fix

* fix(reposcan): set source id to null instead of deleting it ([`613c615`](https://github.com/RedHatInsights/vmaas/commit/613c6150fdb0ecff2dc535f74ffa718728ac4624))

## v1.10.2 (2020-03-23)

### Fix

* fix(reposcan): invalidate webapp cache only when task succeeded (#678) ([`c9befc5`](https://github.com/RedHatInsights/vmaas/commit/c9befc5cc97bbebc9fddddab116f096e4e1775d4))

## v1.10.1 (2020-03-18)

### Fix

* fix: check on system level to find vulnerabilities and workaround pipenv to make it work ([`6c5f6db`](https://github.com/RedHatInsights/vmaas/commit/6c5f6dbab5e21c20ea1bbac6d61c587f0776f1b2))

* fix: Revert &#34;temporarily ignore cve in pipenv&#34;

This reverts commit ec23cb5226ded5d245c3bfce244f190481ad676c. ([`20e535b`](https://github.com/RedHatInsights/vmaas/commit/20e535b37f7f3c4161b941952b372274b2da0fea))

## v1.10.0 (2020-03-18)

### Chore

* chore: add database upgrades unit tests ([`0b698f7`](https://github.com/RedHatInsights/vmaas/commit/0b698f7302d1c678a71b2b39aeb395d437bc217a))

### Feature

* feat(database): add database upgrade scripts and tutorial ([`d5ce37e`](https://github.com/RedHatInsights/vmaas/commit/d5ce37e4b9ae8fd93adab80946ede0e36f5a5565))

### Test

* test: replace commit ref with actual one ([`5645482`](https://github.com/RedHatInsights/vmaas/commit/56454821420688d081063343b98ea6287aeb44f4))

## v1.9.0 (2020-03-12)

### Chore

* chore(reposcan): add pyOpenSSL library ([`e98f563`](https://github.com/RedHatInsights/vmaas/commit/e98f5634835a5a213f2dfb460aac0df622bb5dcf))

### Feature

* feat(reposcan): add function to check cert expiration date ([`857fe35`](https://github.com/RedHatInsights/vmaas/commit/857fe350fa95e1bfe10b9d946b3cde92bd8faee9))

## v1.8.0 (2020-03-11)

### Feature

* feat(webapp): Add autoscaler to webapp, format secrets as a list of yaml values ([`58d7a56`](https://github.com/RedHatInsights/vmaas/commit/58d7a5697874d481163b59c120035b4e2add754b))

## v1.7.0 (2020-03-10)

### Feature

* feat(webapp): add lite error formatter ([`98bacd3`](https://github.com/RedHatInsights/vmaas/commit/98bacd3b0be1e76676bf6ad3a222e50dbf6902b1))

## v1.6.1 (2020-03-09)

### Chore

* chore: remove error formatter ([`abe093b`](https://github.com/RedHatInsights/vmaas/commit/abe093b4faab86c948c1e1895db81214928b4f1c))

* chore: upgrade connexion version ([`f6c7d3b`](https://github.com/RedHatInsights/vmaas/commit/f6c7d3bd96cf8cce61272ef8c8dc67e7d873bd43))

### Fix

* fix: temporarily ignore cve in pipenv ([`ec23cb5`](https://github.com/RedHatInsights/vmaas/commit/ec23cb5226ded5d245c3bfce244f190481ad676c))

## v1.6.0 (2020-03-05)

### Feature

* feat(reposcan): add failed repo-download methrics for different http codes ([`80b71a8`](https://github.com/RedHatInsights/vmaas/commit/80b71a85b758df39e37d9ddaec611c89b67eb39a))

## v1.5.0 (2020-02-26)

### Chore

* chore: jenkinsfile line continuation ([`e4b16bb`](https://github.com/RedHatInsights/vmaas/commit/e4b16bbbc79cf9e56a5138673b6fdd9e52d08dfc))

* chore: run Actions on PR to master/stable, Jenkins against master/stable ([`1017f73`](https://github.com/RedHatInsights/vmaas/commit/1017f73958f5910219f46d951b6469c7af3d4c42))

### Feature

* feat: Add pkgtree API endpoint to webapp (#650)

* Add pkgtree API endpoint to webapp

* fix check_deps_versions to deal properly with dir .

* Add first pkgtree code to webapp

* Add pkgtree API spec to webapp.spec.yaml

* Add pkgtree data format schemA webapp.spec.yaml

* Add pkgtree code for handling get/post requests

* Add additional attributes for webapp pkgtree API

* Add module/stream support for webapp pkgtree api

* Add handling code for webapp pkgtree api

* Remove unused pkgtree tests

* Fix indentation in webapp/pkgtree.py

* Remove TODO from webapp.spec.yaml

* Attempt to make Travis CI pass

* Another attempt to make travic CI to pass

* Add first tests for webapp pkgtree API

* attempt to force running Travis again - infrastructure failure

* webapp pkgtree - first tests  pass

* Add for webapp pkgtree schema tests

* Add more tests for webapp pkgtree API

* Make travis happy

* Ignore some pylint comments for webapp pkgtree tests

* Add to webapp pkgtree getting package details from cache

* Add to webapp pkgtree getting nevras

* Add more test data to webapp/test/data/cache.yaml

* For webapp pkgtree implement getting erratas

* For webapp pkgtree add handling respositories

* For webapp pkgtree implement first_published date

* Remove some todos from webapp

* Add sorting to webapp pkgtree API

* Add webapp natsort dependency to Pipfile

* Add to webapp pkgtree tests for sorting response items

* Cleanup webapp pkgtree and fix more tests.

* Another cleanup in webapp pkgtree

* Update for webapp pipfile.lock with natsort package

* Fix webapp/test/yaml_cache to work with pyyaml 5.3

* Fix some pylint warnings for webapp pkgtree

* Test travis failure

* Add fixed package versions for webapp Pipfile

* Update webapp Pipfile.lock with natsort package

* Fix failing webapp fests after adding pkgtree

* For webapp ignore pylint message about missing natsort module

* Add app tests for webapp pktree

* Revert back webapp yaml cache to full_load ([`b56c681`](https://github.com/RedHatInsights/vmaas/commit/b56c681916919e85d690125e756c2a783a7195df))

## v1.4.4 (2020-02-18)

### Chore

* chore: delete correct pvc ([`3b79649`](https://github.com/RedHatInsights/vmaas/commit/3b796491d422bffa1d7bf30e7dd64862fdf90afb))

### Fix

* fix(reposcan): use left join instead of inner ([`1288da4`](https://github.com/RedHatInsights/vmaas/commit/1288da4d29f2de511353786021085e21db810037))

## v1.4.3 (2020-02-18)

### Chore

* chore: workaround ocdeployer bug ([`54b3e24`](https://github.com/RedHatInsights/vmaas/commit/54b3e24cf0a7b78c853987aa680c595b1d3c0327))

* chore: run jenkins only on master branch ([`503c9dd`](https://github.com/RedHatInsights/vmaas/commit/503c9dddc0e4f44eb77ef1179bb9bc9cb276a50a))

* chore: use github actions for integration tests ([`9087c97`](https://github.com/RedHatInsights/vmaas/commit/9087c97eea08d63d1b86e6f59f4c6d4fa77ef965))

### Fix

* fix(webapp): set 415 error code and change detail message for incorrect content type ([`bd37916`](https://github.com/RedHatInsights/vmaas/commit/bd37916779c55555d63d21c7f47d6d5457a664e5))

## v1.4.2 (2020-02-18)

### Fix

* fix(database): store null severity in errata table

fix(reposcan): import null severity to db

fix(webapp): return null instead of empty string ([`0657527`](https://github.com/RedHatInsights/vmaas/commit/065752791726a28f7f934b3b409ca2a03e6009fa))

## v1.4.1 (2020-01-28)

### Fix

* fix(reposcan): repo is empty string because stdout of git clone is empty

remove assert and rely only on validation below that repo file has been downloaded

related probably to switch to UBI 8 images and newer git version ([`91a7e75`](https://github.com/RedHatInsights/vmaas/commit/91a7e75ab6b297282ca9dc0cbfa9b44cd420bdca))

* fix(reposcan): init logging in Git sync ([`c10fff8`](https://github.com/RedHatInsights/vmaas/commit/c10fff83c7f03c8c0d1fbc976d7d95327d6a8b3d))

## v1.4.0 (2020-01-27)

### Feature

* feat(reposcan): add metrics to count failed imports of cves and repos ([`e17de4d`](https://github.com/RedHatInsights/vmaas/commit/e17de4d5848195593d9b5c6eda7e1db7db978c67))

## v1.3.6 (2020-01-14)

### Chore

* chore: ignore coverage of python modules in /usr ([`3db0299`](https://github.com/RedHatInsights/vmaas/commit/3db0299ddf906e586ad0797acc3115738d78b254))

### Fix

* fix(manifests): fix manifest push process ([`c48d226`](https://github.com/RedHatInsights/vmaas/commit/c48d2268f868760d4be24e6b96d76e130f7a1036))

## v1.3.5 (2020-01-10)

### Chore

* chore: migrate CentOS 7 images to RHEL 8 UBI and obsolete RHEL 7 ([`343365a`](https://github.com/RedHatInsights/vmaas/commit/343365af8c2dd97d3599b409576416874a9aec1b))

* chore: remove obsoleted Dockerfile ([`b924e38`](https://github.com/RedHatInsights/vmaas/commit/b924e380e51d9ec86b8daac904770a0ab64ac882))

* chore: use only RHEL-based Dockerfile ([`5acc5db`](https://github.com/RedHatInsights/vmaas/commit/5acc5db9f6e866395269556e99b094a7287426a7))

* chore: remove obsoleted script ([`f4a6459`](https://github.com/RedHatInsights/vmaas/commit/f4a64593a5e5a552b6bf5cf60b6736f347f9f334))

### Fix

* fix: obsolete Dockerfile diff test ([`9167f22`](https://github.com/RedHatInsights/vmaas/commit/9167f228ac30b6e2a80df1a3df10ba5582204acb))

* fix: obsolete suffixes in OpenShift deployment ([`a9f21fd`](https://github.com/RedHatInsights/vmaas/commit/a9f21fdb69bcd8064f01a05ab951c065420e2523))

* fix(reposcan): xml tree evaluates found elements as False ([`8e7b24e`](https://github.com/RedHatInsights/vmaas/commit/8e7b24edfe3ef172cce709e744c2d067f1ef538b))

### Refactor

* refactor: wait for postgresql without psql ([`510dd5a`](https://github.com/RedHatInsights/vmaas/commit/510dd5a46b2bd9dc1b18e3e514f299182534814d))

## v1.3.4 (2020-01-08)

### Fix

* fix(reposcan): duplicate conflict while importing repos ([`ffd4b00`](https://github.com/RedHatInsights/vmaas/commit/ffd4b00a9e81a79e3b432bc3ee1008df3d9dfd16))

## v1.3.3 (2019-12-18)

### Fix

* fix(reposcan): syntax error while deleting repos ([`a58e48c`](https://github.com/RedHatInsights/vmaas/commit/a58e48c185b0378d67d5ce4993c593444da88c4a))

## v1.3.2 (2019-12-10)

### Fix

* fix(reposcan): delete module by repo fk reference ([`d192ff1`](https://github.com/RedHatInsights/vmaas/commit/d192ff1b4667c8cbc60f7f59c6e4cae07c8e2ede))

## v1.3.1 (2019-12-09)

### Chore

* chore: fix reposcan:/data ownership in devel setup ([`3e42d9e`](https://github.com/RedHatInsights/vmaas/commit/3e42d9e94faba33bfccd57200820687f51835c48))

* chore: jenkinsfile path to tests

Without slash it runs also vulnerability tests because of jenkins workspace path @jdobes was too fast and merged it before my force push :smile: ([`df782e1`](https://github.com/RedHatInsights/vmaas/commit/df782e163aacf7ecafb7ea25a49cdf89fb1175cb))

* chore: update vmaas tests path ([`4dba197`](https://github.com/RedHatInsights/vmaas/commit/4dba197f018ccdff41c7d78c7febc345bab0e8bb))

### Fix

* fix(webapp): fix 500 error when empty modules_list ([`caa6edf`](https://github.com/RedHatInsights/vmaas/commit/caa6edf198ae5b87af1b8b89519c6113c17d8b08))

### Refactor

* refactor(websocket): unify entrypoint in websocket with other containers ([`6e6c8a0`](https://github.com/RedHatInsights/vmaas/commit/6e6c8a0b8597e90a097b8807ff70d5d8a17712c4))

## v1.3.0 (2019-12-03)

### Feature

* feat(webapp): add new version of /updates API

allowing to return all/security updates only based on &#39;security_only&#39; parameter ([`3566ff2`](https://github.com/RedHatInsights/vmaas/commit/3566ff2088c875d55891c38fb8cfad654bd15d4b))

* feat(reposcan): export all updates, not only security ([`2373c48`](https://github.com/RedHatInsights/vmaas/commit/2373c484d956235d4341e736c9110a84c867ba89))

## v1.2.1 (2019-11-27)

### Fix

* fix(reposcan): optimize and fix source package associations ([`9d41a50`](https://github.com/RedHatInsights/vmaas/commit/9d41a50163916e2e19330a0ff00f3d9f1983257c))

## v1.2.0 (2019-11-26)

### Feature

* feat(reposcan): don&#39;t sync CVEs from NIST ([`8d88702`](https://github.com/RedHatInsights/vmaas/commit/8d887020ca6fa00ffa52dfcf923633d4b043b860))

### Fix

* fix(reposcan): store references from cvemap as secondary url ([`8934aac`](https://github.com/RedHatInsights/vmaas/commit/8934aac47431d16507fd96f1d25cadf59999cb8e))

* fix(reposcan): create always pre-defined redhat_url ([`fd2efe8`](https://github.com/RedHatInsights/vmaas/commit/fd2efe8301a1f562097028b3906843317b6d8968))

* fix(reposcan): sync IAVA when available ([`1768ad7`](https://github.com/RedHatInsights/vmaas/commit/1768ad7b8e66a00cff0783961fe42bea4cbbd7ab))

## v1.1.5 (2019-11-26)

### Fix

* fix(reposcan): pkgtree is exported and not synced, fix endpoints ([`f762c46`](https://github.com/RedHatInsights/vmaas/commit/f762c46d0efea3b4795d3342bd03477ade2454b1))

### Unknown

* Change &#34;developer mode&#34; containers startup with PODMAN ([`9bfa3ad`](https://github.com/RedHatInsights/vmaas/commit/9bfa3ad1a6d9fca0d5105d55014fc6cb2c395a34))

* Update podman-compose module and fix mountPoint KeyError ([`eca8bb0`](https://github.com/RedHatInsights/vmaas/commit/eca8bb0c788f56000f1bfa0d5cb4366624eac059))

## v1.1.4 (2019-11-21)

### Fix

* fix(webapp): fix sending message to websocket ([`aa54f0b`](https://github.com/RedHatInsights/vmaas/commit/aa54f0b35f4cb62a26b94d62403c00efc88ecc3e))

### Refactor

* refactor(websocket): add logging ([`ec40163`](https://github.com/RedHatInsights/vmaas/commit/ec40163239cfb0c255abcebfdbfbfed0d9b87e10))

### Unknown

* Don&#39;t fail whole job when some of the tests failed ([`5cf843c`](https://github.com/RedHatInsights/vmaas/commit/5cf843cf2fadc741a0e1b2e161fd9508bad4574d))

## v1.1.3 (2019-11-21)

### Chore

* chore(travis): run on stable branch to generate doc ([`7f8841b`](https://github.com/RedHatInsights/vmaas/commit/7f8841bd21b7c2632540879617f7b462305459b0))

### Fix

* fix(reposcan): revision has to be updated but only sometimes ([`66a4e43`](https://github.com/RedHatInsights/vmaas/commit/66a4e4394b621149473ea905325de464b281d977))

## v1.1.2 (2019-11-20)

### Fix

* fix: correctly display version in swagger ([`c88f0d1`](https://github.com/RedHatInsights/vmaas/commit/c88f0d14621b8d1f1b1c05494bb970bcbfba3211))

## v1.1.1 (2019-11-20)

### Fix

* fix(reposcan): don&#39;t reset timestamp and update only things that make sense ([`153371b`](https://github.com/RedHatInsights/vmaas/commit/153371b084db186b84959cdee0ebc1565c705e17))

## v1.1.0 (2019-11-19)

### Chore

* chore: lock different container due to pipeline-lib-v3 ([`27a1ded`](https://github.com/RedHatInsights/vmaas/commit/27a1dedb071f46842e686dc21bcb6483de070030))

### Feature

* feat(reposcan): Add an api call to load repositories from git ([`92bf0ff`](https://github.com/RedHatInsights/vmaas/commit/92bf0ff056eae701edc56f408c35f80dc6925f68))

### Fix

* fix(reposcan): add missing default CDN cert variables ([`4cdd962`](https://github.com/RedHatInsights/vmaas/commit/4cdd962094fbae813d22b1e6682709012660c87f))

* fix(reposcan): don&#39;t flood logs with error when there is lot of errors

interrupt download instead ([`62fb346`](https://github.com/RedHatInsights/vmaas/commit/62fb34655e027e0faad88bfc248240f6a22646ec))

* fix(reposcan): run git download in periodic sync ([`4d732da`](https://github.com/RedHatInsights/vmaas/commit/4d732da49bd5afc5b84afe8dc23d3036e3f44235))

* fix(reposcan): change endpoint to more appropriate ([`cfb7672`](https://github.com/RedHatInsights/vmaas/commit/cfb7672cd114b4d76f6a6c420cab118e1965d66f))

* fix(reposcan): don&#39;t run export when new (empty) repos are added ([`75d027a`](https://github.com/RedHatInsights/vmaas/commit/75d027acf8e345a50dada03ed9b709f8085d65cf))

* fix(reposcan): fix github access from openshift ([`7949e82`](https://github.com/RedHatInsights/vmaas/commit/7949e82ffae71dc5a12c7f8c6da29559236072c9))

### Unknown

* Do not allocate node until stages start running ([`e585e87`](https://github.com/RedHatInsights/vmaas/commit/e585e8783880351923956abe4596257eabf522ad))

* tests(webapp): Hotfix wrong expected results from tests ([`07a2b50`](https://github.com/RedHatInsights/vmaas/commit/07a2b50bd2b9b71ccb6e39a356c2adc8bce55033))

* Run long running tests against master ([`dbd62ba`](https://github.com/RedHatInsights/vmaas/commit/dbd62baee17013caba83b74015da65f1d8aa5551))

## v1.0.0 (2019-11-15)

### Unknown

* Configure semantic release ([`9bce5bf`](https://github.com/RedHatInsights/vmaas/commit/9bce5bf1e3a1a73637d0a2894e598823e2696e68))

* simplify to not use variable names from input JSON but use single default set if entitlement section is missing

it&#39;s making configuration less complex ([`093896e`](https://github.com/RedHatInsights/vmaas/commit/093896e423dfd96a868e2a91bb86fabbb74e1fd5))

* remove script for listing repositories as it&#39;s going to live in different repo ([`4bf523e`](https://github.com/RedHatInsights/vmaas/commit/4bf523eafd9ec9cf880d6b538ddb9776cec91212))

* Remove old schema validation ([`2600c91`](https://github.com/RedHatInsights/vmaas/commit/2600c91d1fc545ec6d38dd32a239cf8528a45569))

* do not run grafana and prometheus in developer setup ([`b7a3a0b`](https://github.com/RedHatInsights/vmaas/commit/b7a3a0bc9eca9e6dde130442caf2c1ae2b430611))

* allow to use podman for local setup ([`fd08173`](https://github.com/RedHatInsights/vmaas/commit/fd081734db8532f93f65b350c02850c43127aab8))

* additional settings to run developer setup on podman ([`21e3d01`](https://github.com/RedHatInsights/vmaas/commit/21e3d0128aed53f00ba8b84522398184677e76e7))

* Add database generation script and settings ([`3aac2a8`](https://github.com/RedHatInsights/vmaas/commit/3aac2a8f1ccf2045a6faf9d1c439c54f9c9fd49d))

* Rollback the split updates encoding ([`b493fb9`](https://github.com/RedHatInsights/vmaas/commit/b493fb94384b1ba4a81fcd4b7910bc5f4e784aeb))

* use lastest version of insights-pipeline-lib ([`37ef8c7`](https://github.com/RedHatInsights/vmaas/commit/37ef8c7584029c672595f9b3c163664ceeee8707))

* Fix all string concatenation issues + simplify N -&gt; 1 query in errata&#39;s process_list ([`f2fb493`](https://github.com/RedHatInsights/vmaas/commit/f2fb493a0d4db0644bb23f49eec17192bda1ba94))

* Fix bug 500 in webap-utils /errata ([`e7d7efb`](https://github.com/RedHatInsights/vmaas/commit/e7d7efb72482ce0d01af32884481455b280ea883))

* Reduce number of checked packages in /updates logic

This commit changes the way we encode updates, so that there are separate lists for
each architecture instead of one single list. This should reduce amount of packages
we need to traverse in order to find valid updates, and therefore reduce /updates
call latency.

There might be some duplication, since we store duplicate information (noarch packages)
but thius should be on the order of several MBs, maybe tens...

The order of updates for noarch packages might also be slightly altered ([`c40f893`](https://github.com/RedHatInsights/vmaas/commit/c40f893ff2c135bf180fe43800ecbb1c6afd8460))

* rhsm cert is optional (can be passed using env variable to reposcan) ([`58fff59`](https://github.com/RedHatInsights/vmaas/commit/58fff599804beb8425d3a1874c5d264f64262996))

* Manually set metrics Content-Type in reposcan ([`9277d7e`](https://github.com/RedHatInsights/vmaas/commit/9277d7ef2d13ff20b7f8b0c5023ea981859514c8))

* Deduplicate strings in database dumps, use array for pkg_details ([`54f60ee`](https://github.com/RedHatInsights/vmaas/commit/54f60ee2729446fb82f869ed635f273b68f0d019))

* Use arrays for storing list[int] ([`f82c5aa`](https://github.com/RedHatInsights/vmaas/commit/f82c5aa7213ca7e782733871d882e5317d6714f2))

* delete apispec dependency ([`46dbae5`](https://github.com/RedHatInsights/vmaas/commit/46dbae508ef4388c5f3965a46a8f06e9457873e0))

* Remove useless apidoc test ([`ac9c1fe`](https://github.com/RedHatInsights/vmaas/commit/ac9c1fe04c93dd7c4e9ad52bb7967011d1b95346))

* Remove apidoc container its remains ([`b2f4345`](https://github.com/RedHatInsights/vmaas/commit/b2f43455fcec29aafa69f879aa39edf6caea69ec))

* Fix dependencies in webapp-utils ([`7966bf1`](https://github.com/RedHatInsights/vmaas/commit/7966bf1f88614b72e3a85f4f88bc96dedbe4b1a2))

* Fix 500 when request not json ([`c45f031`](https://github.com/RedHatInsights/vmaas/commit/c45f031850beeccc826b0d029dffa66d7ae34ac2))

* pin insights-pipeline-lib version ([`a855da2`](https://github.com/RedHatInsights/vmaas/commit/a855da2a97458ac9b0784a7a18a0e82331532fc8))

* Fix 500 in error_formater ([`efbfa58`](https://github.com/RedHatInsights/vmaas/commit/efbfa58880ae14bb2a844740b5c2726d0ae686db))

* Fix module common not found error ([`5883280`](https://github.com/RedHatInsights/vmaas/commit/5883280d3da3a26811242995fc3a0b98cf75556a))

* Edit webapp spec to match the jsons inside .py files ([`7005516`](https://github.com/RedHatInsights/vmaas/commit/700551678b5a6e984738d148450a3fb6c7b59dbd))

* Add json error formatter for connexion json errors ([`b415ce3`](https://github.com/RedHatInsights/vmaas/commit/b415ce3e5d1acf50416b5016c7d2d4291cbaec1f))

* Provide metrics endpoint as text/plain, only log constant part of the path ([`06fa7df`](https://github.com/RedHatInsights/vmaas/commit/06fa7dfb8e736410f9e163f8813a775cb5bc693f))

* Fix signal handlers killing application in combination with multiprocessing

Disables the signal handlers when creating new multiprocessing pools, so that they don&#39;t inherit custom  handlers.
Also kill multiprocessing pool on receiving signal. ([`2b66434`](https://github.com/RedHatInsights/vmaas/commit/2b664348a469433af7ffcc34cf07d9bb6bf511c1))

* Utils packages api bugfix and new get method ([`d8c0cd5`](https://github.com/RedHatInsights/vmaas/commit/d8c0cd54759b825452caa2d4e164cd94f8805d33))

* workaround for old pinned version

PR with updated pins to iqe-tests is submitted but it is not merged yet ([`a088e7b`](https://github.com/RedHatInsights/vmaas/commit/a088e7b05b79333c9f5296cc4968a01267d564f8))

* Handle HttpError in handle_request ([`991cbd7`](https://github.com/RedHatInsights/vmaas/commit/991cbd7975076881cd95cffe88502b498df16792))

* collect openshift logs in jenkins job ([`cdded85`](https://github.com/RedHatInsights/vmaas/commit/cdded85ef8fdb69ba0a18a0204111e989869ff12))

* NotSet is not used in cvemap.xml, None is ([`b738be4`](https://github.com/RedHatInsights/vmaas/commit/b738be4f2520e24fadf9c99a09be71e834179809))

* Fix issues pointed out by new version of pylint ([`efce200`](https://github.com/RedHatInsights/vmaas/commit/efce200495eca12d0cac667544115096277ec19a))

* Optimize _get_repositories method in updates API ([`ee2b5aa`](https://github.com/RedHatInsights/vmaas/commit/ee2b5aae3dc09aaa2fa47bfca4a54a9168e0cadd))

* Fixed references to webapp entrypoint ([`daef381`](https://github.com/RedHatInsights/vmaas/commit/daef381e8a0a9fae6e2aa3baa5d0f8707998cd5b))

* Fix tests and formatting erros that were caused by migration to connexion ([`19eb172`](https://github.com/RedHatInsights/vmaas/commit/19eb172ab609cecfb75ed3f844d2e235bc2b4f8f))

* Migrate webapp to connexion &amp; aiohttp

This change completely removes tornado, and replaces it with connexion,
and its aiohttp backend. By utilizing aiohttp, we preserve the performance
gained by using async handlers, and by utilizing connexion we get better
documentation &amp; data validation. ([`f45da57`](https://github.com/RedHatInsights/vmaas/commit/f45da572a31c9eff7e6d294a7874dd83e7a74f87))

* Create API spec

the webapp.spec.yaml contains OpenApi 3.0 specification of the API provided by webapp
component, it was based on the Swagger 2.0 specification that was generated by Apispec ([`c5a7683`](https://github.com/RedHatInsights/vmaas/commit/c5a7683c20352100edd9f7dd29d5913473be84bd))

* Accept repomd entries without size ([`c06a4c6`](https://github.com/RedHatInsights/vmaas/commit/c06a4c60bac14ebeafb45d1387651a52bf13e214))

* Change logging style in webapp-utils. ([`827f0f9`](https://github.com/RedHatInsights/vmaas/commit/827f0f9ad2c9716f4742e2213df1270cf383deb9))

* Refactorization of webapp/webapp-utils. ([`2edbbae`](https://github.com/RedHatInsights/vmaas/commit/2edbbae8504f88c114cd91cf67066a5fb94148d7))

* pagination restriction improves speed of sql select ([`b339dba`](https://github.com/RedHatInsights/vmaas/commit/b339dba72d361999ef3dfe903dca88ea3e24f43f))

* errata select separated to specific functions ([`e80374f`](https://github.com/RedHatInsights/vmaas/commit/e80374f6026cebaef458c75e8ca542acd5261212))

* add full text search errata function ([`10972ce`](https://github.com/RedHatInsights/vmaas/commit/10972ce137409a600b50061ef0d61424cf698859))

* Create Errata API in webapp_utils - POST/GET methods. ([`9c83996`](https://github.com/RedHatInsights/vmaas/commit/9c83996b6d058a4a37d58968c74cd6b3588c9bdb))

* Add new items returned in packages/repositories API. ([`656e37c`](https://github.com/RedHatInsights/vmaas/commit/656e37cf6f2ce33c0e80c7da45e4b55a79f3d83e))

* Add tests for /v1/packages/repostories API ([`71a33d4`](https://github.com/RedHatInsights/vmaas/commit/71a33d47896c75dbc444d971deefaeb1e01db597))

* Add /v1/packages/repositories API ([`a22cc86`](https://github.com/RedHatInsights/vmaas/commit/a22cc8629486d1dc26e6ff5eccb08f2a33826b90))

* Add webapp_utils packages API tests. ([`1c530f2`](https://github.com/RedHatInsights/vmaas/commit/1c530f2e5babcb8e1515f449ca9b07087ca4a7aa))

* Add /v1/packages webapp-utils API. ([`7c91d16`](https://github.com/RedHatInsights/vmaas/commit/7c91d1690679f586bfe9f58fcd5ec3816de3d837))

* Re-implement basic API endpoint tests

These utilized tornado.testing.AsyncHTTPTestCase. This was replaced by base_case.py,
which provides pytest fixtures, and utility methods.

Fix security scheme to accept github formatted Authorization: token &lt;token&gt; header

Remove unnecessary base.py, and clean up the reposcan code ([`6eb9369`](https://github.com/RedHatInsights/vmaas/commit/6eb936967352e751bad0b60c2baaced612ecf696))

* Remove unneded dependency on apispec ([`28042af`](https://github.com/RedHatInsights/vmaas/commit/28042af5c7161040aecc08ca438bdfe037ae49e2))

* Adapt base.py to vmaas codebase, remove unnecessary doc-comments ([`013a57e`](https://github.com/RedHatInsights/vmaas/commit/013a57e5db80fa4762922ccb9c97f9dded03b512))

* Added basic implementation of reposcan based on connexion

This uses similar approach to the one used in vulnerability engine, with individual API calls being
implemented in classes, with basic behavior implemented in base classes from base.py. The server uses
WSGI container running on tornado, which contains the application, since we require the IOLoop for
current implementation of websocket client. ([`a1ccdcf`](https://github.com/RedHatInsights/vmaas/commit/a1ccdcf3735443fd95b6776e4a40d3dd71e7b53b))

* Import base.py from vulnerability-engine codebase ([`0dcb162`](https://github.com/RedHatInsights/vmaas/commit/0dcb162caf70b654a62c0403e72266a1054dcc75))

* add common directory to containers in docker-compose.devel.yml ([`baa5e84`](https://github.com/RedHatInsights/vmaas/commit/baa5e842c386ff463a86030eeedb193e06f7b330))

* Fix backslashes ([`68871bb`](https://github.com/RedHatInsights/vmaas/commit/68871bbc57a2fea74eee057871579df3688f3719))

* fix rhel7 Docker files for podman-compose ([`4850cb6`](https://github.com/RedHatInsights/vmaas/commit/4850cb61fb3e54060af717a445d946f2ed0cafd6))

* fix Docker files for podman-compose ([`14f86b5`](https://github.com/RedHatInsights/vmaas/commit/14f86b5295bb5648a8a69fc57167df5990c3d73a))

* Fix missing files in Dockerfile-qe ([`c544b06`](https://github.com/RedHatInsights/vmaas/commit/c544b060e530c649f3f7d63f3fadc2655de96142))

* errata endpoint provides info about module updates ([`4e26de6`](https://github.com/RedHatInsights/vmaas/commit/4e26de64cc915ef2d2647cdeea26a11848250423))

* Refactoring of common utilities for vmaas parts ([`9ba8390`](https://github.com/RedHatInsights/vmaas/commit/9ba83905e2c4b25f5eea9a246f116ab209cb39e8))

* Make batching behavior configurable, and dependant on available disk size

The batching can be configured using BATCH_MAX_SIZE and BATCH_MAX_FILESIZE env variables.
Reposiories are processed in batches that are at most BATCH_MAX_SIZE large, and consume at most
BATCH_MAX_FILESIZE bytes on disk. The information about unpacked repo sizes is retrieved from repomd.xml files. ([`5639bb6`](https://github.com/RedHatInsights/vmaas/commit/5639bb68695bac5052da8e5d2343979139b9a3bf))

* make sure always latest image is pulled ([`51201af`](https://github.com/RedHatInsights/vmaas/commit/51201af676f573530b625ad506ee9c64c1eab412))

* don&#39;t update images ourselves ([`9e2aed5`](https://github.com/RedHatInsights/vmaas/commit/9e2aed5050339105845eadd9cb6b620afdfa42e0))

* use python as everywhere else ([`364da40`](https://github.com/RedHatInsights/vmaas/commit/364da40b4a85b6540c2e9a2dac88cd74f98a1b00))

* Make GH organization for authorized API endpoints configurable ([`b233456`](https://github.com/RedHatInsights/vmaas/commit/b2334563f7e472544a1742ad2280d39ff09dbef1))

* Add pkgtree_change item in dbchange get API. ([`552ebf0`](https://github.com/RedHatInsights/vmaas/commit/552ebf0741aacc7bde6a13d7ebc567a9db9a290e))

* add pre-hooks to make sure manifest git always have running deployment ([`bb7e408`](https://github.com/RedHatInsights/vmaas/commit/bb7e408c761916f7c094c51d55f290c9c0f4880a))

* add bot secret ([`a7773f6`](https://github.com/RedHatInsights/vmaas/commit/a7773f6cb53ad6e1f7fb116068b80481ee1af952))

* gracefully stop services ([`e1977b5`](https://github.com/RedHatInsights/vmaas/commit/e1977b5fef5d7da86d23f61867576aa93ba58396))

* fix generating pipfile manifest ([`99a8530`](https://github.com/RedHatInsights/vmaas/commit/99a85306713791c6eb245151759860c79130e2f4))

* no need to install git ([`f816097`](https://github.com/RedHatInsights/vmaas/commit/f8160970f73d8855f9d5170b829928c964a5a641))

* change push script to commit using github API ([`545322f`](https://github.com/RedHatInsights/vmaas/commit/545322f6e3e31407d982c165951d28f395af42ce))

* fix incorrect parameter ([`7d5012d`](https://github.com/RedHatInsights/vmaas/commit/7d5012daf1b2fd636f0f0a0ba09209c6a9c9047a))

* create script for pushing manifests and include it in containers ([`1f47fef`](https://github.com/RedHatInsights/vmaas/commit/1f47fef8b20c989e94031e75c0cdd70d4676f5c8))

* include only relevant RPMs in manifest ([`c8e5f84`](https://github.com/RedHatInsights/vmaas/commit/c8e5f8488d39346b3690471f14027091682cb657))

* fix warning about missing LANG ([`dc90fcb`](https://github.com/RedHatInsights/vmaas/commit/dc90fcbbbaa77c3e00e2e63528d71fccaa25c74b))

* optimize dockerfiles, add code at the end ([`9c8df0f`](https://github.com/RedHatInsights/vmaas/commit/9c8df0f22a512c9662af191d18542ef9b0aed215))

* don&#39;t log on default level because of too many messages ([`dbac8f9`](https://github.com/RedHatInsights/vmaas/commit/dbac8f991467892828e9ddd45862e1e5e2a0df31))

* fix duplicated results ([`67fa961`](https://github.com/RedHatInsights/vmaas/commit/67fa9619d610ffe3a5c668c79eaad0ecafbbebcc))

* used generic prometheus metrics and labels ([`fb3a036`](https://github.com/RedHatInsights/vmaas/commit/fb3a0365ca47ceb4a90a7550299a76cc630ea218))

* unified BaseHandler.handle_request method ([`5d75512`](https://github.com/RedHatInsights/vmaas/commit/5d75512316a7ec020c8f89bfe8b05a43ca68378a))

* added generic request log message using on_finish method ([`954c055`](https://github.com/RedHatInsights/vmaas/commit/954c055527e4319d0650e7a7cb1d174ecdb764c8))

* added filter for (none) in manifest generator ([`a6e3fa4`](https://github.com/RedHatInsights/vmaas/commit/a6e3fa440e5f317a8363b97f92efabe0ad058ad5))

* used faster way to check python updates using pur

replaced previous method &#34;pipenv update --dry-run&#34; ([`a0d8053`](https://github.com/RedHatInsights/vmaas/commit/a0d8053a0ecb1beda787f3b4a48e909daa25212e))

* fixed webapp tests after pytest version upgrade ([`9ba3e50`](https://github.com/RedHatInsights/vmaas/commit/9ba3e500556633feb0649a361600f1c07d898af9))

* updated deps (Pipfile and Pipfile.lock files) ([`22238b3`](https://github.com/RedHatInsights/vmaas/commit/22238b36634f218a9c95e38570ec4910a07adfee))

* added pipenv for dependency management ([`2d29a7d`](https://github.com/RedHatInsights/vmaas/commit/2d29a7dd3af7f94bd538f158becdc25a7f701d42))

* used Fedora 28 instead of Fedora 27 for testing

Fedora 27 (python 3.6, postgresql 9)
Fedora 28 (python 3.6, postgresql 10) ([`e8a79e1`](https://github.com/RedHatInsights/vmaas/commit/e8a79e136fe24f58e9ef090179a97cdcd47e050f))

* Fix duplicate values ([`a46f370`](https://github.com/RedHatInsights/vmaas/commit/a46f3706ccce4ee83d1ee981354268a27a9aece4))

* vmaas support for SSL certificates in reposcan ([`5f693b9`](https://github.com/RedHatInsights/vmaas/commit/5f693b9036aeae2cb915040c2e76a4ebf00f418a))

* webapp_utils added to devel docker-compose, changed entrypoint, updated docs ([`5e69709`](https://github.com/RedHatInsights/vmaas/commit/5e69709e94dd743e19a5a168fe2fee15ae8dc0cc))

* added tests including tilda and caret in nevra ([`2c6ae61`](https://github.com/RedHatInsights/vmaas/commit/2c6ae618d04c8919395800a3257759ad83aa9140))

* added tilda and caret to accepted characters in query param

packages like my-pkg-1.0.0~beta and my-pkg-1.0.0^ were rejected
with UpdatesAPI as tilda and caret were not included in accepted
characters in path definition ([`7dc075c`](https://github.com/RedHatInsights/vmaas/commit/7dc075cdd068f8578d09374904fb55a8beab44c2))

* Add few reposcan and webapp unit-tests. ([`b611b75`](https://github.com/RedHatInsights/vmaas/commit/b611b75e9d105376ea5f123196ca957a9a684912))

* added metrics guide to doc ([`648433d`](https://github.com/RedHatInsights/vmaas/commit/648433d7132520e30d1e3bef40f59e49e6afd491))

* added grafana to docker-compose ([`1458ace`](https://github.com/RedHatInsights/vmaas/commit/1458acee6f81bd7f8fd537607f615605a239f3b5))

* added prometheus to docker-compose ([`1ae8618`](https://github.com/RedHatInsights/vmaas/commit/1ae86183de3d1126b8cfb653daf5f56dc2edf174))

* updated deps if possible ([`27cfa63`](https://github.com/RedHatInsights/vmaas/commit/27cfa63e8fe9eb2de76062cd56f4a8b7c72ee99b))

* added deps versions checking using pur ([`dc64394`](https://github.com/RedHatInsights/vmaas/commit/dc64394bce384aac82227168feb0e6c6b36b75eb))

* added pur package to testing deps ([`f84f1ef`](https://github.com/RedHatInsights/vmaas/commit/f84f1ef17b265a20e01f242a349450623cf53e36))

* added manifest to the component images ([`be85052`](https://github.com/RedHatInsights/vmaas/commit/be8505254979e530ce37731ba9778d27e8fd19ae))

* Add working API docs with connexion and working app. ([`23d48aa`](https://github.com/RedHatInsights/vmaas/commit/23d48aa3a7cd6b47c3c6e0f561ebb9b587ec9499))

* Add new container for webapp utilities API. ([`27d4280`](https://github.com/RedHatInsights/vmaas/commit/27d4280239117a06af3ceb16eabd96466ebb3fc1))

* Add remove_file_if_exists common util function ([`2de37f7`](https://github.com/RedHatInsights/vmaas/commit/2de37f776dcbff23dfc26f4ff6f5691b61e9bbfc))

* better NamedCursor error handling ([`428e680`](https://github.com/RedHatInsights/vmaas/commit/428e68049ca6048a1796275248f8f53a197e1f9c))

* Update errata and cve tests ([`910ac1a`](https://github.com/RedHatInsights/vmaas/commit/910ac1a16ed1873aad4b76da5ee1aa79c669dbc7))

* Add tests ([`40d51b4`](https://github.com/RedHatInsights/vmaas/commit/40d51b4c8c12430de3739d30bc04b0a6d0f8bfca))

* Fix filtering by modified since ([`904cf00`](https://github.com/RedHatInsights/vmaas/commit/904cf0040f8ffe5e21ee8a5bd11600cdb3459541))

* Fix page size in repos api ([`7e1dc9d`](https://github.com/RedHatInsights/vmaas/commit/7e1dc9db2749a6df74c198c3297dd95874661cb1))

* Readme.md upgraded with process of starting vmaas up in developer mode ([`0d51fee`](https://github.com/RedHatInsights/vmaas/commit/0d51feebceb337bd59e711918a6ec64c28938237))

* fix module parsing ([`58fe38d`](https://github.com/RedHatInsights/vmaas/commit/58fe38d52789aa34d7a7035a1e014bc41cea5c20))

* Add LABEL for repo sync failures logs. ([`4a8cacd`](https://github.com/RedHatInsights/vmaas/commit/4a8cacd7b8db34e21aa1818266174871f50d5dec))

* workaround simple-rest-client version ([`5b8584b`](https://github.com/RedHatInsights/vmaas/commit/5b8584b5f9101f2921b864e3038cf2329605f9b7))

* refactor jenkinsfile ([`d2425de`](https://github.com/RedHatInsights/vmaas/commit/d2425def4e81e50f895319a6dce56d1a6f42fee9))

* added manifest generator script ([`fa7ea9f`](https://github.com/RedHatInsights/vmaas/commit/fa7ea9f2a3d8e0e3b3feb9e3089321ae78caaa4f))

* fixed missing values in swagger CvesResponse ([`286ed1c`](https://github.com/RedHatInsights/vmaas/commit/286ed1c5e46e74cb859316f5528bc9b1efbf8c06))

* increased reposcan sync frequency

changed REPOSCAN_SYNC_INTERVAL_MINUTES from 720 to 360 ([`0c88d70`](https://github.com/RedHatInsights/vmaas/commit/0c88d7059eca1993004e56b84a57c72bc30390d3))

* updated .coveragerc for reposcan and websocket to exclude test sources ([`f096ae9`](https://github.com/RedHatInsights/vmaas/commit/f096ae990da980c67c3650e3b14e57bbda320836))

* removed skipping test_errata.py test_modified_since ([`34e6aa5`](https://github.com/RedHatInsights/vmaas/commit/34e6aa551b2b36119c0f0a90808474742a93d9a6))

* webapp - exceptions in GET handler completed ([`632be57`](https://github.com/RedHatInsights/vmaas/commit/632be57e336fe10485cdfa395ad2e59f421f5efb))

* added websocket initialization test ([`94d5718`](https://github.com/RedHatInsights/vmaas/commit/94d5718e53506a28538affd659de25fd8425a071))

* added mocked websocked tornado test ([`64214bc`](https://github.com/RedHatInsights/vmaas/commit/64214bc12254e1b32f993a96767663bc9496df1d))

* added websocket tornado test ([`b78f9da`](https://github.com/RedHatInsights/vmaas/commit/b78f9da45f6d9336156c1446d640d8078640f7e2))

* Allow filter CVEs by published_since parameter. ([`d7d7491`](https://github.com/RedHatInsights/vmaas/commit/d7d7491ce42b4725e999ecb46f17c1b69b339bc4))

* fix and reuse common rpm.parse_rpm_name() method ([`aa88b98`](https://github.com/RedHatInsights/vmaas/commit/aa88b98e5a7ad2f4a1f40ec89806d695449c341b))

* added webapp init process test ([`0864719`](https://github.com/RedHatInsights/vmaas/commit/086471985709f4ef83fd416fbaec9dbe9ad7354a))

* added cache test ([`12b9401`](https://github.com/RedHatInsights/vmaas/commit/12b9401a46e5471db7525ec8aea867c538641802))

* added webapp endpoint tests ([`8f42192`](https://github.com/RedHatInsights/vmaas/commit/8f42192ca520e59b7c591a0a724e7a91001d283e))

* added cvemap_store.lastmodified check ([`2a5429a`](https://github.com/RedHatInsights/vmaas/commit/2a5429a120cb04a37540bedb19311f356b4a2b11))

* added reposcan init process test ([`94b2b97`](https://github.com/RedHatInsights/vmaas/commit/94b2b9787350ba493c2da54afd40349517d99b41))

* added reposcan integration test ([`78d3c34`](https://github.com/RedHatInsights/vmaas/commit/78d3c34481a815fab266cd470a5067673a7d73de))

* added reposcan tornado app endpoints tests ([`137e8fc`](https://github.com/RedHatInsights/vmaas/commit/137e8fc4388d2cee18763f4138f32e8d50ed57a1))

* added pkgtree module test ([`01d2fe7`](https://github.com/RedHatInsights/vmaas/commit/01d2fe78d9c6701e36f67bfdd93b410daf7700e3))

* updated updateinfo.xml file

added updated timestamps
added cve reference types ([`256d9b8`](https://github.com/RedHatInsights/vmaas/commit/256d9b85c722e0af6fe3c4fd5096ee9eab57d9da))

* added modules loading test ([`4f39dad`](https://github.com/RedHatInsights/vmaas/commit/4f39dad47523fe240c351c0eb27b08089a30fc3b))

* added test for ProgressLogger ([`a9b4214`](https://github.com/RedHatInsights/vmaas/commit/a9b42144408d96349fa7f2b4131ee21283b843bd))

* Disable concurrent builds

Use Lockable Resource Plugin to lock openshift vmaas-qe project resource while tests are running. ([`2523b89`](https://github.com/RedHatInsights/vmaas/commit/2523b89f20424cc1a673125f3cfa4581a5364d52))

* added schema ([`bef4c1a`](https://github.com/RedHatInsights/vmaas/commit/bef4c1a366ee00638af5b360547cb92fe80e03cc))

* python3 replaces (python) in README.md ([`1e9a9f9`](https://github.com/RedHatInsights/vmaas/commit/1e9a9f97c17a5f5d9e421d776a5e785fea50b834))

* remove modified_since from response

When modified_since was not specified in request

fix tests ([`d0dbdc9`](https://github.com/RedHatInsights/vmaas/commit/d0dbdc9443316dc82264c8d054d426227565727b))

* fix codecove upload from testing docker container ([`46b7c3e`](https://github.com/RedHatInsights/vmaas/commit/46b7c3e2a54fd757c78b319e49e33b4ebb4b97c7))

* remove modules profiles storage.  Its not needed and because it also inserts into package_name table, it causes duplicate inserts (db constraint violations) with package_store that also inserts into package_name. ([`e22a908`](https://github.com/RedHatInsights/vmaas/commit/e22a90847f2524a2587a39defcebeed07ee1a2e9))

* pylint fixes ([`ece271e`](https://github.com/RedHatInsights/vmaas/commit/ece271e166ea860b0f5523f4f56a3d564bdad40c))

* Address PR comments ([`9817d06`](https://github.com/RedHatInsights/vmaas/commit/9817d0655bb415d112d75f265d27f93a1b1ef269))

* update to support better db error handling ([`52d61fa`](https://github.com/RedHatInsights/vmaas/commit/52d61fa0f8c8326b3e20a3bcdf8be8e30dd196ca))

* add modules to pkgtree output ([`6f72b1b`](https://github.com/RedHatInsights/vmaas/commit/6f72b1b5dc1714e5dff9313f013b4c33c0424afe))

* Revert &#34;don&#39;t sync initial module state&#34;

This reverts commit 43c79ed7c2b830853da9b6aa82170501e0c38c64. ([`77da57b`](https://github.com/RedHatInsights/vmaas/commit/77da57b9906e0b39adba7fe3f519e837a74983e3))

* correct omitting of /opt in Jenkinsfile

Now, when it is not executed using scl-enable.sh, --omit path should not be in quotes. ([`fe2afdf`](https://github.com/RedHatInsights/vmaas/commit/fe2afdf360d0558ee3016f927e50ba48a98d54e0))

* Add test for filter_item method ([`690904c`](https://github.com/RedHatInsights/vmaas/commit/690904c2536ab31095524f75e5508aebf06ab6b1))

* Make method filter_item_if_exists simplier ([`987c034`](https://github.com/RedHatInsights/vmaas/commit/987c0340daaa28f5b9b3679a806343da1ab77ee3))

* Corrects by PR review

To utils/ add unified filter to check existance ([`21625ff`](https://github.com/RedHatInsights/vmaas/commit/21625ffcd65b86a17bb90ffca20185b4bbc46a75))

* Add filters to check if exist repos, cves and errata ([`518a0f3`](https://github.com/RedHatInsights/vmaas/commit/518a0f388fcea4fa51799e3e7894c5c315467636))

* Separate condition which checking modified since date in repos to separate filter ([`1957ce1`](https://github.com/RedHatInsights/vmaas/commit/1957ce1e2eede62e0ae161e71f3004bca8f25b4a))

* removed useless sql functions &#39;isdigit&#39;, &#39;isalpha&#39;, &#39;isalphanum&#39;

functions were used in previously removed sql function &#39;rpmver_array&#39;
now they are useless so they are removed ([`10cadbb`](https://github.com/RedHatInsights/vmaas/commit/10cadbb0f71f02a305d60caccbdc7dc7beffc724))

* add symlink for coverage command ([`69b49a2`](https://github.com/RedHatInsights/vmaas/commit/69b49a2f65918384af9c8d5f2f86b4933e340d19))

* updated webapp-qe dockerfile path in Jenkinsfile ([`3b9ff8d`](https://github.com/RedHatInsights/vmaas/commit/3b9ff8d5f08950c7512fe62fb37c4e8055e90afd))

* upated scripts/new-release.sh script

updated dockerfiles paths
extended help message
extended updating log messages ([`79d3c64`](https://github.com/RedHatInsights/vmaas/commit/79d3c6480b5e686c0ec32029b5613b321601edbe))

* updated openshift configs ([`ad6836c`](https://github.com/RedHatInsights/vmaas/commit/ad6836c91d05e28e244f4b519b873289bd09f059))

* component dockerfiles moved to subfolders ([`d71a70d`](https://github.com/RedHatInsights/vmaas/commit/d71a70dc5ecb508106d6b2333a524a8668fc7a90))

* simplified components Dockerfiles

removed scl-enable.sh usage
removed APPBASEDIR env var ([`ce68249`](https://github.com/RedHatInsights/vmaas/commit/ce68249a75d9aa0d7bded94581db0785a2d736a2))

* use RHEL images default ([`9b75dbf`](https://github.com/RedHatInsights/vmaas/commit/9b75dbf23996387fab800c00084019b44796c393))

* pylint fixes ([`69d0a0b`](https://github.com/RedHatInsights/vmaas/commit/69d0a0b485f9e3ab4d165fd4b0e08b9739391072))

* Handle db errors gracefully during scan ([`4468521`](https://github.com/RedHatInsights/vmaas/commit/44685219dc9697185ab7715d658bc42b853501ce))

* srpms of source packages have None/empty srpm field ([`0ee1855`](https://github.com/RedHatInsights/vmaas/commit/0ee1855caefcfd22bc1988e1ee68f7b4a97ea7e7))

* added rpm name to RPMParseException ([`3f62744`](https://github.com/RedHatInsights/vmaas/commit/3f627443230e28611b3d5ffd55ee6d54e20973bd))

* added &#34;package_list&#34; field to /api/v1/packages

info about binary packages built from given source package ([`9c545d8`](https://github.com/RedHatInsights/vmaas/commit/9c545d8447428d62754a960f7940a804a2390bb4))

* added src_pkg_id2pkg_ids mapping to exporter

exported mapping of &#34;source package id&#34; to &#34;bin package ids&#34; ([`82a2f90`](https://github.com/RedHatInsights/vmaas/commit/82a2f905010ad451d6125edd8430947ebfdbfd69))

## v0.13.0 (2019-06-12)

### Unknown

* fix source rpm epoch

get source rpm epoch from binary rpm if
no source rpm epoch provided in primary repo data ([`7c04c8d`](https://github.com/RedHatInsights/vmaas/commit/7c04c8d53c54967f70df6dcb74920e19aec959f8))

* simplified README.md

- joined multiple following commands using ~~~bash
notation
- improved some formating ([`4558148`](https://github.com/RedHatInsights/vmaas/commit/455814820dc5e84155557ad1650cabd5f99a691f))

* removed unused sql function rpmver_array ([`4c55b0b`](https://github.com/RedHatInsights/vmaas/commit/4c55b0b777416754523aac2d0bc665a2f29a9df1))

* added support for ~ and ^ notation

sql function rpmver_array replaced with python one
added several tests for related functions ([`ee1a20e`](https://github.com/RedHatInsights/vmaas/commit/ee1a20ee22f8b626bb41708c5635a8cf188122fb))

* fixed webapp /repo API endpoint example ([`bb2781b`](https://github.com/RedHatInsights/vmaas/commit/bb2781b614ca41fcb2c77d8537626ee24414821a))

* removed github-fetch-pullrequest script, packed to PyPI ([`c71b4cd`](https://github.com/RedHatInsights/vmaas/commit/c71b4cd5b64d9cbe4a4f529419683f22a27f6ffc))

* updated tests (cve, errata, package, utils)

for using source packages info ([`73792ab`](https://github.com/RedHatInsights/vmaas/commit/73792abeddd30e76568a8368ced7a23a6853135f))

* added source package info to errata, cve and package API ([`0d3a848`](https://github.com/RedHatInsights/vmaas/commit/0d3a848725bc80aac55f1fb9036eca9cfebb06b0))

* added some testing packages from primary.xml to updateinfo.xml

to enable pkg_errata pairing ([`0dd92b9`](https://github.com/RedHatInsights/vmaas/commit/0dd92b91d7e1a8c6bf160b39650ba75a277f672a))

* added testing source package to cache.yml ([`f2886eb`](https://github.com/RedHatInsights/vmaas/commit/f2886eba84e96e0086fd727b12cd2d1ba5fba9fe))

* fixed webapp tests to use simplified cache.yml ([`a5aabf0`](https://github.com/RedHatInsights/vmaas/commit/a5aabf06055ba9828f8bb78494393d98ea613dc9))

* manually simplified cache.yml ([`60003bd`](https://github.com/RedHatInsights/vmaas/commit/60003bdeeae71bcf8a86913a166d48069b462c85))

* there are only security-related package IDs in dump ([`23bd463`](https://github.com/RedHatInsights/vmaas/commit/23bd46355c1514dac8df2156b088d6d3e6482af1))

* don&#39;t check IDs directly, they may be different after DB regeneration ([`8ccc6af`](https://github.com/RedHatInsights/vmaas/commit/8ccc6af3d82529e489bfc56907c99d688ac3b413))

* regenerate test data ([`c4e2866`](https://github.com/RedHatInsights/vmaas/commit/c4e2866608b19456ab068c2892af63da1bc9538f))

* source_package_id needs to be extracted ([`de67db9`](https://github.com/RedHatInsights/vmaas/commit/de67db94de330f467d80ec926197886ddac96f2a))

* add modified_since to the response ([`3fbacad`](https://github.com/RedHatInsights/vmaas/commit/3fbacadb20b858af2f0cc9086971986b95f2aebf))

* optimized Dockerfile.test

removed duplicit sources adding
added separated requirement.txt files adding to enable caching ([`953cb43`](https://github.com/RedHatInsights/vmaas/commit/953cb43660007c0498f0aa0a6bbcb7bb7a0e1aef))

* fixed KeyError populating also source_packages dependent tables ([`793ed05`](https://github.com/RedHatInsights/vmaas/commit/793ed0511a4dca419b1f0e5f7e330d10d038cce2))

* rpm module moved to common package ([`9577f6f`](https://github.com/RedHatInsights/vmaas/commit/9577f6f2e96926253348fc6f766bf3e39b5fda1a))

* added writing source packages to packages table ([`cdbc4d5`](https://github.com/RedHatInsights/vmaas/commit/cdbc4d5d9ab4466b1d970efff8b3ba782108ea18))

* added srpm field to package when reading primary.xml or primary.sqlite ([`0e256ca`](https://github.com/RedHatInsights/vmaas/commit/0e256ca55bf9d3be4e44a6d7b875a59edc38d549))

* renamed table srpm to source_package ([`aa6f169`](https://github.com/RedHatInsights/vmaas/commit/aa6f1693a7b226dc1186ca939dfe75eba32fa438))

* added rpm name parsing using regex ([`aac1761`](https://github.com/RedHatInsights/vmaas/commit/aac176169eaa711267cb5a2d968e8f682b0022a2))

* added srpm info writing to database ([`735582c`](https://github.com/RedHatInsights/vmaas/commit/735582ce04c868ed15798ff67d2ca13174bfff54))

* extended test_primary to check more things ([`a12a84c`](https://github.com/RedHatInsights/vmaas/commit/a12a84cfef33cb486f42b4f5ff543e2f67dd01c2))

* fix counting up-to-date repos ([`9b45918`](https://github.com/RedHatInsights/vmaas/commit/9b45918ff59ac263be03f27b84e5b9f8a28ad873))

* add better progress logging ([`1d8357a`](https://github.com/RedHatInsights/vmaas/commit/1d8357ac198a6553f8cf360126cffa9be18eb713))

* there is only one nevra now ([`d28accc`](https://github.com/RedHatInsights/vmaas/commit/d28accc027a25edc11c83da6dadf7b3b2ad11223))

* delete package checksum from test data ([`31e3d91`](https://github.com/RedHatInsights/vmaas/commit/31e3d919896aba85d10e9323c2eadb40a30a2ef1))

* don&#39;t extract checksum from primary ([`c6c7e8b`](https://github.com/RedHatInsights/vmaas/commit/c6c7e8bef8e6242fd273dfb0b0969f2658ada26f))

* populate packages based on unique nevra ([`4c74018`](https://github.com/RedHatInsights/vmaas/commit/4c740182a846e3b80f21b2245e998b811b6165ae))

* drop package checksum from schema ([`4c99cf6`](https://github.com/RedHatInsights/vmaas/commit/4c99cf6617bb3de19acd3d1e477ff5b9e7ba1ad9))

* simplified code using generic &#34;_populate_dep_table&#34; method

used instead of multiple methods per each table ([`d96f57e`](https://github.com/RedHatInsights/vmaas/commit/d96f57e6ca9d8db09515b4d3347bd42c0223216f))

* Revert &#34;Fix traceback when importing repos w/modules and without at the same time&#34;

modules_store code is not used

This reverts commit c6e89e3d7727ed81409e01c3b4619bad4de3fd46. ([`3258fc2`](https://github.com/RedHatInsights/vmaas/commit/3258fc2ac82cdf1b53474c6debea2c2263dd0e1b))

* simplified code using generic &#34;_prepare_table_map&#34; method

replaced several _prepare... methods with generic one ([`9a673ea`](https://github.com/RedHatInsights/vmaas/commit/9a673ea635616045903a5db96e1ba7d9041ce5c2))

* don&#39;t sync initial module state ([`43c79ed`](https://github.com/RedHatInsights/vmaas/commit/43c79ed7c2b830853da9b6aa82170501e0c38c64))

* disable sync of initial module states ([`f339a9a`](https://github.com/RedHatInsights/vmaas/commit/f339a9abc97d95a4ada5d7c49418001d6303624b))

* Coverage is needed in webapp-qe dockerfile ([`1ecba53`](https://github.com/RedHatInsights/vmaas/commit/1ecba53a5a68d705d633a02d27d77733578adf6c))

* used fedora:27 as the testing docker image ([`1517f87`](https://github.com/RedHatInsights/vmaas/commit/1517f87c5cf898a238f66efbc48ee9c37d1d1169))

* removed useless python spec from travis conf

tests are run using docker so no python is needed in env ([`df11c6b`](https://github.com/RedHatInsights/vmaas/commit/df11c6bfdb216a1d390a38e9302d5cb10fef9417))

* added travis tests running using docker-compose ([`4fb4539`](https://github.com/RedHatInsights/vmaas/commit/4fb4539ebac7320af1d45cb4226398bea94a2483))

* added cache files ignoring using .gitignore ([`5383216`](https://github.com/RedHatInsights/vmaas/commit/5383216e404c558d374809dac1ad1f8fc90dec35))

* added slowest tests duration to tests output ([`0d4751c`](https://github.com/RedHatInsights/vmaas/commit/0d4751c64e4152d3e78c289ea436c6c81291443b))

* colorized pylint output ([`40f0d07`](https://github.com/RedHatInsights/vmaas/commit/40f0d07077a58d4f947c11250208cfd75362589d))

* renamed tests running service ([`dcff6f1`](https://github.com/RedHatInsights/vmaas/commit/dcff6f1b51564da29aeba1f01ebad92afc65fb18))

* updated tests running guide ([`7e18755`](https://github.com/RedHatInsights/vmaas/commit/7e187555b10cf26ea584434158689801e3c6d5b4))

* used requirements.txt files in Dockerfiles ([`be92485`](https://github.com/RedHatInsights/vmaas/commit/be92485415d2147079bdb52478ef6b573fc62566))

* deps classified to right requirements files, removed useless deps ([`ccbac34`](https://github.com/RedHatInsights/vmaas/commit/ccbac347afaceb3c6dd83cc822e1ce3473299376))

* added deps with locked versions into requirements.txt files ([`8f52acf`](https://github.com/RedHatInsights/vmaas/commit/8f52acf5aa1167b3e07ce8beaf32f7d2d35f72a7))

* fixed yaml.load to yaml.full_load to remove warning ([`64a1c59`](https://github.com/RedHatInsights/vmaas/commit/64a1c59b593a8df4367ca121d661e4bc893b6fb3))

* added tests running using docker-compose.test.yml ([`d1abc51`](https://github.com/RedHatInsights/vmaas/commit/d1abc513be2a7f2ee589572fe7874d6041c6f0e0))

* create API for getting repositories that changed after certain date ([`c8af470`](https://github.com/RedHatInsights/vmaas/commit/c8af470acbde429f7ff8ca514b472309495954d0))

* add reposcan exporter unit tests ([`1dd76d0`](https://github.com/RedHatInsights/vmaas/commit/1dd76d002faf0c09306a8cd5cba0099671acc936))

* add coveragerc files ([`d366faa`](https://github.com/RedHatInsights/vmaas/commit/d366faa64c541bca1b68a383269b0d40bdc316b3))

* Fix unique-constraint-violation error when importing repos with modules with errata

- Remove pkg_errata_pkg_id_errata_id_key
- Add pkg_errata_pkgid_errataid and pkg_errata_pkgid_streamid_errataid to
  a) add module_stream_id to uniqueness while b) correctly dealing with its null-ness ([`2738bc2`](https://github.com/RedHatInsights/vmaas/commit/2738bc2f0e7f6f2d5fbd5385c5f353c7390b3a53))

* Fix traceback when importing repos w/modules and without at the same time

Import creates known-package-map at startup and assumes nothing can change it inside a single run.
Modularity-related code violates that assumption.

Teach package_store to not rely on __init__-time processing so much. ([`c6e89e3`](https://github.com/RedHatInsights/vmaas/commit/c6e89e3d7727ed81409e01c3b4619bad4de3fd46))

* renamed var &#34;m&#34; to &#34;mod&#34; because of pylint rules ([`00cd209`](https://github.com/RedHatInsights/vmaas/commit/00cd209685c7afab0e3eb2342817b2663bebc347))

* fixed comment ([`57a418d`](https://github.com/RedHatInsights/vmaas/commit/57a418d79033180548a92158e8c68b9e82e114f3))

* added repodata.modules test ([`ea449b0`](https://github.com/RedHatInsights/vmaas/commit/ea449b070948c0b0dcbca040a635e7ef0961ef4a))

* replaced yaml.load method with yaml.full_load

because of security issue in yaml.load method
allowing code execution ([`2409d86`](https://github.com/RedHatInsights/vmaas/commit/2409d86104aff79c4db9b0ea95e5997782828b68))

* don&#39;t instantiate new UpdatesAPI each call

by instantiating a new object each call all caching was made uselles
as after one API call the cached things were garbage collected ([`fbd65fa`](https://github.com/RedHatInsights/vmaas/commit/fbd65fa570bb2393b1e589ff543250f680e13f87))

* add probe for # of inserts into cache ([`3032c53`](https://github.com/RedHatInsights/vmaas/commit/3032c535ba681d0c869ebc686b18d457c1a8bb61))

* add more diagnostics for /updates ([`3e8e3fb`](https://github.com/RedHatInsights/vmaas/commit/3e8e3fbe8c4b69818bb681ba8426c1c74dd3481a))

* update pr fetch script ([`68ccc48`](https://github.com/RedHatInsights/vmaas/commit/68ccc48a3317bc0dc7b2d89b81a72acd7177ba9f))

* add probes for /updates hot cache hits/misses ([`9c61bac`](https://github.com/RedHatInsights/vmaas/commit/9c61bac53b16bbcc57e347961b007d9674ff4676))

## v0.12.0 (2019-04-23)

### Unknown

* create new API for applicable CVEs to a package list ([`8333bf0`](https://github.com/RedHatInsights/vmaas/commit/8333bf00f4265e93374a96546b37422d0ccc912d))

* Fix #473 - move to PostgreSQL 10 ([`055a60c`](https://github.com/RedHatInsights/vmaas/commit/055a60c156d069a5cd10cb4cba2f5ec40a9c1aef))

* reduce number of intermediate images after code change ([`a680dfa`](https://github.com/RedHatInsights/vmaas/commit/a680dfa3e8d2a577df94d2eca5a22dace4fd7bc5))

* check RHEL and CentOS Dockerfiles for differences ([`f7b7037`](https://github.com/RedHatInsights/vmaas/commit/f7b703798a91aaddf5e0709d1afb916ea55ad55f))

* catch missing parts of module info during json schema validation

vmaas-webapp       | f44bdb3ffc28 2019-04-04 08:13:25,084 __main__: [ERROR] Internal server error &lt;-9223363243124068951&gt;: please include this error id in bug report.&#39;Traceback (most recent call last):\n  File &#34;/webapp/app.py&#34;, line 105, in handle_post\n    res = api_endpoint.process_list(api_version, data)\n  File &#34;/webapp/updates.py&#34;, line 381, in process_list\n    module_info = [(x[\&#39;module_name\&#39;], x[\&#39;module_stream\&#39;]) for x in modules_list]\n  File &#34;/webapp/updates.py&#34;, line 381, in &lt;listcomp&gt;\n    module_info = [(x[\&#39;module_name\&#39;], x[\&#39;module_stream\&#39;]) for x in modules_list]\nKeyError: \&#39;module_stream\&#39;&#39;|
vmaas-webapp       | f44bdb3ffc28 2019-04-04 08:13:25,084 __main__: [INFO] Input data for &lt;-9223363243124068951&gt;: {&#39;package_list&#39;: [&#39;postgresql-9.6.10-1.el8+1547+210b7007.x86_64.rpm&#39;], &#39;modules_list&#39;: [{&#39;module_name&#39;: &#39;postgresql&#39;}]} ([`e06177d`](https://github.com/RedHatInsights/vmaas/commit/e06177d4ee942c1ef307adbbe38377ae123f0c8f))

## v0.11.0 (2019-04-02)

### Unknown

* Ignore /opt instead of /usr ([`49ceefd`](https://github.com/RedHatInsights/vmaas/commit/49ceefd43b7eaf855116f6bb84107704ebea9233))

* fix coverage ([`0355547`](https://github.com/RedHatInsights/vmaas/commit/035554779a6305641360a4ac1076e3c567ebecd3))

* Delete vmaas-db persistent volume ([`36a3dd7`](https://github.com/RedHatInsights/vmaas/commit/36a3dd71e6ece79e0d91ad9d4bb64c9a9163852e))

* Notify with custom context ([`76ddd36`](https://github.com/RedHatInsights/vmaas/commit/76ddd36f97b998e620b2983c21096ccc09027ce1))

* Use centos dockerfile ([`5b806ea`](https://github.com/RedHatInsights/vmaas/commit/5b806ea666c5e4cfba97f19e580f4fd1a345a5ec))

* Change env to build images according to changes in e2e-deploy

https://github.com/RedHatInsights/e2e-deploy/pull/97 ([`35cf1b1`](https://github.com/RedHatInsights/vmaas/commit/35cf1b1f25d3b429efc0f504958a19a39cbf7ae9))

* Fix travis - missing &#39;yaml&#39; module ([`17cd7c0`](https://github.com/RedHatInsights/vmaas/commit/17cd7c0faf9cb25ed159e827af34ff8c3bda9abc))

* Re-run webapp&#39;s app.py ([`6acbe30`](https://github.com/RedHatInsights/vmaas/commit/6acbe30e6d77587acfbd26eb1396b9151129469b))

* entrypoint-qe permissions ([`04cebdf`](https://github.com/RedHatInsights/vmaas/commit/04cebdf1e20ebfd9fb545b9df967cbed85530b4d))

* Get correct git reference ([`679fec0`](https://github.com/RedHatInsights/vmaas/commit/679fec05f818eb495b718e521bdb11812a6c2737))

* Revert &#34;Build containers from master&#34;

This reverts commit 8b753bf6d55e75d37ac56ead9e10c2c512de87c9. ([`25a695d`](https://github.com/RedHatInsights/vmaas/commit/25a695da3c7cfd785ae2bcb50bba7e9a7fbbc977))

* Build containers from master ([`075961c`](https://github.com/RedHatInsights/vmaas/commit/075961c863a63fa924d6e06c6df29b0c4ce4d2eb))

* QE Dockerfile

Don&#39;t run app.py, but `sleep infinity`. Web application will be triggered from Jenkins pipeline as `coverage run app.py`, thus we can collect coverage of integration tests. ([`5048c45`](https://github.com/RedHatInsights/vmaas/commit/5048c45ef5cda5635e6423d9eb6915f95e36b3b0))

* Add Jenkins pipeline ([`8ce7398`](https://github.com/RedHatInsights/vmaas/commit/8ce7398a866dec5e59c7d53b65d43effb11b3cb8))

* return module information in the /updates response if there&#39;s any ([`5538009`](https://github.com/RedHatInsights/vmaas/commit/5538009be5cabe24bcef8c56b3c4200699524bc4))

* VMAAS-328 - Expose webapp/reposcan to prometheus ([`5f7c4fa`](https://github.com/RedHatInsights/vmaas/commit/5f7c4fab103484e539fdf80585bf77cb8b9daa84))

* VMAAS-328 - missed a pylint warning ([`d5fde2f`](https://github.com/RedHatInsights/vmaas/commit/d5fde2fb7f1c3bf2c081ffbd8fbb36352e5a02de))

* VMAAS-328 - Add more monitoring to vmaas

This adds the basic framework to reposcan. However, the majority of
the work reposcan does happens in asycn children, which are separate
processes from the parent; their counts do not make it up to
MetricsHandler. A future task needs to teach reposcan&#39;s controllers
how to export their info. ([`507a986`](https://github.com/RedHatInsights/vmaas/commit/507a9861128f501e9a39116f9be914a3927cde31))

* #456 - recognize that NIST-json can be utf-8 ([`29d7249`](https://github.com/RedHatInsights/vmaas/commit/29d72499307e8ef3f03deddaf69ac64667af5889))

* add codecov badge ([`8865b92`](https://github.com/RedHatInsights/vmaas/commit/8865b92ec01692a2f614f35d7d8a669514eb9c6c))

* add unit tests for modularity ([`5326c7a`](https://github.com/RedHatInsights/vmaas/commit/5326c7abd6d4d25a940b2a9e61648caac0495500))

* satisfy pylint after tornado 6.0 update ([`2e139f4`](https://github.com/RedHatInsights/vmaas/commit/2e139f4cd017c8dc434ce329f2dba9e98cd3b640))

* always clean data in temp ([`e9d5eac`](https://github.com/RedHatInsights/vmaas/commit/e9d5eac3eabfdadeb8251130007c2e5244734d1a))

* erratas may introduce new module N:S:V:C, store them ([`718ab34`](https://github.com/RedHatInsights/vmaas/commit/718ab340adfff4207933eb3561d674aa4cc42140))

* take repo_id into account when doing lookup for modules ([`7711082`](https://github.com/RedHatInsights/vmaas/commit/7711082f811bc2ce44dc0e5d49a82f579aba77d8))

* process modular updates ([`3f868f4`](https://github.com/RedHatInsights/vmaas/commit/3f868f4ee38c0e3ab004415ee8d87fe4f6366a94))

* export module errata info based on pkg,module pair ([`8d78226`](https://github.com/RedHatInsights/vmaas/commit/8d7822625eec378f92cba08bf4a05fb5029a505b))

* module_stream ID is needed instead of module_id ([`12babef`](https://github.com/RedHatInsights/vmaas/commit/12babef64e071551104c3fd464d8da42e858e60e))

* some module RPMs are not part of the repodata ([`e4abd6a`](https://github.com/RedHatInsights/vmaas/commit/e4abd6a70d729e78db87f8f1e9c0122396ae9b1f))

* search for module rpms in right data structure ([`e8b2206`](https://github.com/RedHatInsights/vmaas/commit/e8b2206d8dad2b57195b85759f3abce8115b36a0))

* export modularity information into disk dump ([`68c393c`](https://github.com/RedHatInsights/vmaas/commit/68c393c1b893f3ca4b92c0ec4eea0836817a43db))

## v0.10.0 (2019-02-21)

### Unknown

* Teach new_release about new locations of Dockerfiles ([`24e6c81`](https://github.com/RedHatInsights/vmaas/commit/24e6c8132fcdd3ddb7ad9e4b1039bc467700a6f7))

* fix import of erratas with same packe multiple times in it ([`53fc06b`](https://github.com/RedHatInsights/vmaas/commit/53fc06bcf23fce95efd0f8cd5320541ae315bd89))

* fix sync failures during package,errata,module disassociation

vmaas-reposcan     | d7b89bc1eb60 2019-02-19 20:22:55,745 database.repository_store: [INFO] Syncing repository: rhel-6-server-cf-tools-1-rpms, x86_64, 6.10
vmaas-reposcan     | d7b89bc1eb60 2019-02-19 20:22:55,747 database.object_store: [INFO] Syncing 31 packages.
vmaas-reposcan     | d7b89bc1eb60 2019-02-19 20:22:55,751 database.object_store: [INFO] Syncing packages finished.
vmaas-reposcan     | d7b89bc1eb60 2019-02-19 20:22:55,765 database.object_store: [INFO] Syncing 4 updates.
vmaas-reposcan     | d7b89bc1eb60 2019-02-19 20:22:55,770 __main__: [ERROR] Internal server error &lt;-9223363290841971384&gt;&#39;Traceback (most recent call last):\n  File &#34;/reposcan/reposcan.py&#34;, line 641, in run_task\n    repository_controller.store()\n  File &#34;/reposcan/repodata/repository_controller.py&#34;, line 255, in store\n    self.repo_store.store(repository)\n  File &#34;/reposcan/database/repository_store.py&#34;, line 173, in store\n    self.update_store.store(repo_id, repository.list_updates())\n  File &#34;/reposcan/database/update_store.py&#34;, line 292, in store\n    self._associate_packages(updates, update_map, repo_id)\n  File &#34;/reposcan/database/update_store.py&#34;, line 148, in _associate_packages\n    (tuple(to_disassociate),))\npsycopg2.ProgrammingError: operator does not exist: integer = record\nLINE 1: ...rrata where (pkg_id, errata_id, module_stream_id) in (((200,...\n                                                             ^\nHINT:  No operator matches the given name and argument type(s). You might need to add explicit type casts.\n&#39;| ([`f30a5d6`](https://github.com/RedHatInsights/vmaas/commit/f30a5d6f1b90d0b341c4ad137f1eadae048bc112))

* psycopg2-binary needed for webapp ([`f785a4d`](https://github.com/RedHatInsights/vmaas/commit/f785a4d0abf9ac3e95078bf1299a52ecb8002396))

* temporarily run on apispec 0.39.0 until we migrate to 1.0 ([`49883ce`](https://github.com/RedHatInsights/vmaas/commit/49883ce1d659c447f61a1a13e5d520d1d0f365a4))

* when openshift deployment is executed with tag &#39;rhel-containers&#39; deploy rhel containers instead of centos ([`9b20bb6`](https://github.com/RedHatInsights/vmaas/commit/9b20bb6426a62887dc52226b1fca5221738904eb))

* apispec is fetched from pypi now ([`dc9b583`](https://github.com/RedHatInsights/vmaas/commit/dc9b5836c9eb63d606238276708a1ede5fdf1773))

* websocket: support centos and rhel in container ([`a6bb00a`](https://github.com/RedHatInsights/vmaas/commit/a6bb00a8827580cc18da55fb63df8833776c43ed))

* webapp: support centos and rhel in container ([`9931f8f`](https://github.com/RedHatInsights/vmaas/commit/9931f8f2866608e297628b5d30c41f71a5e7cea4))

* webapp: remove unmaintained script ([`7f2ae6d`](https://github.com/RedHatInsights/vmaas/commit/7f2ae6d3ed3cba4907b0e2722c6bbe1938f4ed39))

* reposcan: support centos and rhel in container ([`204dcd5`](https://github.com/RedHatInsights/vmaas/commit/204dcd594b457900e2c14a9684429a1cba764a81))

* database: support centos and rhel in container ([`587d7e5`](https://github.com/RedHatInsights/vmaas/commit/587d7e5bee6e9d476301bb980851b814f3f25b25))

* database: delete unused dockerfile ([`1b592c0`](https://github.com/RedHatInsights/vmaas/commit/1b592c064828b9e6f0bd8ffa0e23a95792c64a6a))

* apidoc: move dockerfile to top level directory together with other dockerfiles ([`c9f6085`](https://github.com/RedHatInsights/vmaas/commit/c9f60855439021573b6162cf8bf3fee6fd24296e))

* gather module information from updateinfo ([`48a5d20`](https://github.com/RedHatInsights/vmaas/commit/48a5d20ecd4fc1b511aa658516f7f7698fb89d26))

* store module context

modules are distinguished by N:S:V:C ([`3d47790`](https://github.com/RedHatInsights/vmaas/commit/3d47790ed3d96ca54a8fca36c9e56e25b3ad7236))

* fix non-consistent modulemd and modulemd-defaults

fixes cases when modulemd-defaults were referecing not exisitng
streams/profiles ([`80bf377`](https://github.com/RedHatInsights/vmaas/commit/80bf377adf1a35bce38c6fc437631fa0d764ccef))

* store messages and send them later in case of websocket outage

same thing as in reposcan, eventual disconnects from webscoket
when we&#39;re about to write in it are not handled well ([`db47f0b`](https://github.com/RedHatInsights/vmaas/commit/db47f0b25e4fc8d7b2200434f4c61877043a74c4))

* store messages if websocket is not available and send them once it&#39;s up

if webscoket wasn&#39;t available at the time sync task finished the application
raised a traceback and stopped responding to all other sync requests returning
HTTP 429 to all requests until that sync task was manually cancelled

this commit adds storing message into a queue in case ws is not available
and automatic sending of all messages which should have been
sent in the meantime ([`3949ad7`](https://github.com/RedHatInsights/vmaas/commit/3949ad7fc54c46a3b5254e2c5988bbc2c5efc520))

* store module version information

modules come with version, store it into database as well
so we can track differences between their versions ([`4e579eb`](https://github.com/RedHatInsights/vmaas/commit/4e579ebbb2714c13225019f74e6bd87bbda8c3de))

* fix script to work with authenticated API ([`367a819`](https://github.com/RedHatInsights/vmaas/commit/367a8195b879105c0a1263390602ac1477a4b801))

* some modules do not have rpm artifacts at all ([`140e4e4`](https://github.com/RedHatInsights/vmaas/commit/140e4e43b44e31df4872471eaa692101c260bef9))

* parse modulemd-defaults once we know all modules ([`e88fc99`](https://github.com/RedHatInsights/vmaas/commit/e88fc9949a264a6d2f9134fd69deecf776ad2c31))

* prometheus probe tweaks

 - Added probe to v2/updates (oops)
 - Added Histogram to cve/errata/repos (in addition to /updates)
 - Renamed invocations-counter to make it more clear when collected by the prom-server ([`a0cb9df`](https://github.com/RedHatInsights/vmaas/commit/a0cb9dff16883789346d58002dc1348b3289754f))

* run only python 3.6 ([`db2c34a`](https://github.com/RedHatInsights/vmaas/commit/db2c34a6a6bdbe0e33e939db73137a9a5f3fc666))

* pylint: disable arguments-differ check on tornado method ([`b2b180e`](https://github.com/RedHatInsights/vmaas/commit/b2b180ec79e21c525f3a008a82404da2c2a6823b))

* add prometheus_client ([`daf79f2`](https://github.com/RedHatInsights/vmaas/commit/daf79f28644cfc454b6f8dcb4a466eb23fa69d0d))

* page_size returns actual number of items returned ([`45212b0`](https://github.com/RedHatInsights/vmaas/commit/45212b06af24ad553970693c2d9efd2d65f47dc9))

* fix pytest version ([`191b33b`](https://github.com/RedHatInsights/vmaas/commit/191b33b014d0d0523301f25cfe04149d7919242b))

* fix memory leaks in coroutines

it&#39;s not needed to call &#34;yield self.flush()&#34;, self.flush() is called automatically from self.finish() which is automatically executed in each request ([`a91d526`](https://github.com/RedHatInsights/vmaas/commit/a91d5266044e72929781beefd1982172f114efe6))

* improve pagination when filtering values ([`14df56d`](https://github.com/RedHatInsights/vmaas/commit/14df56df9253e060173e8f5dc8132e33007d0da9))

* Teach webapp to respond to /metrics with prometheus data ([`20cef27`](https://github.com/RedHatInsights/vmaas/commit/20cef2737403bec7cdc5893b879043717d186ea5))

* Add support for Prometheus monitoring to webapp ([`d56aba3`](https://github.com/RedHatInsights/vmaas/commit/d56aba3da75b5051f4025f692fd6e7ba1bd55f1a))

## v0.9.0 (2018-12-19)

### Unknown

* add option to show only Red Hat CVEs ([`9f7f172`](https://github.com/RedHatInsights/vmaas/commit/9f7f172146c75a75771838fb7a640a737e1e6110))

* export cve_source as well ([`bd5da87`](https://github.com/RedHatInsights/vmaas/commit/bd5da8728531cd20b00229cb09fabd2d6a80f0ef))

* Fixed spec to use objects instead of hardcoded ([`956f828`](https://github.com/RedHatInsights/vmaas/commit/956f828b9a910ea4c41836122941050027176b03))

* DB tests are order-dependent - switch schema to not-break tests ([`d1a3ab3`](https://github.com/RedHatInsights/vmaas/commit/d1a3ab3463919543f7515ffb09aa3743f8d4e658))

* Update test-data to handle existence of cvss2 info ([`089cd9e`](https://github.com/RedHatInsights/vmaas/commit/089cd9e4ae67ced4d7fb5bdcaf3c48ed17ebf0f6))

* Teach webapp how to extract cvss2 from cache and return it as part of /cve API ([`4088fe9`](https://github.com/RedHatInsights/vmaas/commit/4088fe91526f26fa7724585d924cfe57484106d8))

* Teach reposcan to extract cvss2 from NIST and RH maps, and export that data ([`4a816de`](https://github.com/RedHatInsights/vmaas/commit/4a816de9dc6fe5538da438ccf90c2bec355f5312))

* Add cvssV2 to CVE in schema ([`e6502e6`](https://github.com/RedHatInsights/vmaas/commit/e6502e63a0c0fb8529be8e6955d207eb3348a0b8))

* pylint: remove unnecessary pass ([`a62e96b`](https://github.com/RedHatInsights/vmaas/commit/a62e96b32debb0a04b3c42d3c4cc59502a6baa03))

* TestBatchList.test_batch_creation was just wrong - fixed the test ([`0181ca3`](https://github.com/RedHatInsights/vmaas/commit/0181ca3949a2f31cd771a567a01ea0f16f4100d4))

* Fix #428 - lower BATCH_SIZE defaults to avoid disk-full issues ([`caf9a27`](https://github.com/RedHatInsights/vmaas/commit/caf9a27fb9c608c2c30bd49c56e28629bbdbf715))

* Raw-download is ignoring Content-Encoding header in transfers ([`001361f`](https://github.com/RedHatInsights/vmaas/commit/001361f75cb3332ca4aac9eca01a4ce9399762c1))

* Install testing.postgresql ([`33175de`](https://github.com/RedHatInsights/vmaas/commit/33175def65235daf8fbeee3db043a466235ebc4f))

* Add tests for DB module ([`61cc88f`](https://github.com/RedHatInsights/vmaas/commit/61cc88f5adbccaaaaafcb4086fd66423dd6022a6))

* Add tests for common module ([`36d73c3`](https://github.com/RedHatInsights/vmaas/commit/36d73c3236b4d29a4159dade4e257b1cdb65cf5a))

* Update run_tests and travis config ([`f5b64a6`](https://github.com/RedHatInsights/vmaas/commit/f5b64a6acc95bcfdadc5a4f0c1a02e9f07b360f6))

* remove duplicated env variable setting

API_URLS env variable was both defined in Dockerfile and conf/apidoc.env ([`62762fd`](https://github.com/RedHatInsights/vmaas/commit/62762fd1cd50b59d26f7334ea205c97e7ca1194a))

* Compatibility with python &lt; 3.6 ([`7e03a13`](https://github.com/RedHatInsights/vmaas/commit/7e03a13ad3323ff9e661ed272a9786755d5536f4))

* Add conftest.py to whitelist &amp; ignore that tests for websocket are missing ([`fdb4e49`](https://github.com/RedHatInsights/vmaas/commit/fdb4e494b1cb271406a0878bdec94e2f8a41f15d))

* Mark cache.yml as generated so it won&#39;t appear in statistics ([`5fe6504`](https://github.com/RedHatInsights/vmaas/commit/5fe650496a09ef60ad1737c9223e48c8c5bea01b))

* Fix travis ([`39b40c4`](https://github.com/RedHatInsights/vmaas/commit/39b40c4211cbf02809ca0daaf029ffae0bb9065b))

* Add webapp unit tests ([`0770552`](https://github.com/RedHatInsights/vmaas/commit/0770552e595e37d7b91f4824bf986f2a21076bca))

* Run tests using pytest &amp; collect coverage ([`eabf2e4`](https://github.com/RedHatInsights/vmaas/commit/eabf2e4618443e42cc9747af79a9392b74ce0e7d))

* ignore vscode project settings ([`456784d`](https://github.com/RedHatInsights/vmaas/commit/456784dd7f81d35b607fe19eb2ff9ecd2ef2b96f))

* Fix #411 - adding &#34;exported&#34; to the dbchange api docs ([`c530c46`](https://github.com/RedHatInsights/vmaas/commit/c530c465a240cde036b0fb4a289726177f4d3dab))

## v0.8.0 (2018-10-17)

### Unknown

* Fix #417 - copy env vars to openshift template ([`1bff77a`](https://github.com/RedHatInsights/vmaas/commit/1bff77a71590ab487491d57c02661021bfe924a6))

* Fix #417 - make pylint happy ([`f17c299`](https://github.com/RedHatInsights/vmaas/commit/f17c29979a39ac95ac2fe92ef693d76e76e1235f))

* Fix #417 - make pkgtree/db-export &#39;keep copies&#39; to be env-vars instead of hardcoded ([`612c94a`](https://github.com/RedHatInsights/vmaas/commit/612c94a2d08e6aea9792de63d68d1b2c91dc3177))

* fix examples ([`60374d6`](https://github.com/RedHatInsights/vmaas/commit/60374d668901f794366d9bcdeae6704f4bb994c4))

* add websocket server to openshift deployment script ([`e99db5a`](https://github.com/RedHatInsights/vmaas/commit/e99db5a10fe68a5fee87b834198c811818941778))

* add missing PKGTREE_INDENT config variable ([`e30a006`](https://github.com/RedHatInsights/vmaas/commit/e30a0065276e15f1320eafb94e7f0374068920c7))

* add websocket openshift config ([`fa8996d`](https://github.com/RedHatInsights/vmaas/commit/fa8996da1dc870be0fe47e4a681adceb70b76007))

* make sure websocket server is up in code as well ([`2340b51`](https://github.com/RedHatInsights/vmaas/commit/2340b513b9b44184b288f7b60d2260eaeed28535))

* run tests on websocket dir ([`64a1fd4`](https://github.com/RedHatInsights/vmaas/commit/64a1fd43904872416b9ec6cd415b5173ce051c20))

* remove websocket server from reposcan and fix url ([`ea00fa2`](https://github.com/RedHatInsights/vmaas/commit/ea00fa2ffe4025f3e3feefe5c02edc60889feecc))

* create vmaas-websocket service ([`bb3f92f`](https://github.com/RedHatInsights/vmaas/commit/bb3f92f29b4453ba395ba82f3972a2c1c483338f))

* make CVSSv3 vector string available in CVEs API ([`3dfbcc4`](https://github.com/RedHatInsights/vmaas/commit/3dfbcc4bd4516e0112bbb14d03b06f109ac1c593))

* sync and export CVSSv3 vector string ([`b0a15f8`](https://github.com/RedHatInsights/vmaas/commit/b0a15f8d2e4fdc047fd58ac0978485bc81150945))

* identify webapp and listener connections and send confirmation to listener once all webapps are refreshed ([`3f82885`](https://github.com/RedHatInsights/vmaas/commit/3f82885baf7335c4f7818144bcfe8d1fc8e8987d))

* set unified docker compose project name to run different composes on same network ([`fb6e8d1`](https://github.com/RedHatInsights/vmaas/commit/fb6e8d1d858392c925c0ddb6d6f8349f8de978c5))

* cleanup obsoleted code ([`b3ce38a`](https://github.com/RedHatInsights/vmaas/commit/b3ce38a5c9d57f71892f9117662c22428b3288dd))

* release app_id version must be specified, don&#39;t try to create unique names based on git hash ([`f7533c9`](https://github.com/RedHatInsights/vmaas/commit/f7533c997f12447ee1dd651f867d5b307b865c3d))

* create additional upgrade step - upgrade-cleanup to keep previous deployment available after upgrade finish

for eventual rollback ([`4c19772`](https://github.com/RedHatInsights/vmaas/commit/4c197722e44f96afb1e1562fc7aec0edee964765))

* change update-images -&gt; rebuild-images as they are built directly in OS ([`5475d7f`](https://github.com/RedHatInsights/vmaas/commit/5475d7f3b3c0aed62267c968deb84c820ae01b53))

* use pre-generated openshift templates instead of patching kompose output

and build directly from git, don&#39;t rely on dockerhub ([`25aea4f`](https://github.com/RedHatInsights/vmaas/commit/25aea4fb89cc476e48e9340b675291c38b2292b0))

* fix #398 - use vmmas_ prefix to not conflict with other names ([`fca09c8`](https://github.com/RedHatInsights/vmaas/commit/fca09c86f11a6b84e55e66fae29b5ca1ad01ec60))

* Add env var support for pkgtree indent.  Defaults to 0 which minimizes size of pkgtree file. ([`1f7e3a5`](https://github.com/RedHatInsights/vmaas/commit/1f7e3a57fc4717ba2de1048598e0d0cdf2199e7d))

* gzip pkgtree ([`ea74a37`](https://github.com/RedHatInsights/vmaas/commit/ea74a377aa4b39bcc426603583e3a12af7bb53e0))

* store module metadata into database ([`f255820`](https://github.com/RedHatInsights/vmaas/commit/f2558207fe0fa1f5f98806b8fd5913baec5d9fbd))

* extract methods which are to be used by module_store into common parent class ([`9944281`](https://github.com/RedHatInsights/vmaas/commit/9944281feb0a58d04c65ed7a281df20fee913aa3))

* parse module metadata and store it into dictionary structure ([`ad9ece4`](https://github.com/RedHatInsights/vmaas/commit/ad9ece4d975203a607bee0027e3532283a7ffd30))

* add database schema for storing modules

some of the tables do not honor 2NF for sake of simplicity as it&#39;s
highly unlikely that these tables will have &gt; 1000 rows ([`fa1ec5e`](https://github.com/RedHatInsights/vmaas/commit/fa1ec5ee94b89b192a96f0d780bbb5a50596cf47))

* Fix pkgtree export when repo.basearch_id is null ([`3133d99`](https://github.com/RedHatInsights/vmaas/commit/3133d99e53d571ff3756010c7867d16eb95b5a57))

## v0.7.0 (2018-09-17)

### Unknown

* add comments on environment variable for the database container.

Environment variables with username and password are used to create a new account in the DB. ([`a220786`](https://github.com/RedHatInsights/vmaas/commit/a2207860a881b3ba519157ef2b970d3bd353e630))

* remove workaround as webapp is based on newer version of tornado now ([`8efd0fe`](https://github.com/RedHatInsights/vmaas/commit/8efd0fe072740023f7efce4d536e526130d14d5b))

* refactoring - move apispec definitions into module ([`00b2eb2`](https://github.com/RedHatInsights/vmaas/commit/00b2eb2b55c287e3fc00722d9fef8d48ff75f6af))

* don&#39;t notify webapps if we only importing repos or creating pkgtree ([`28311e0`](https://github.com/RedHatInsights/vmaas/commit/28311e0b6813538dac48da11a30ba9e0828bf8a2))

* make repository import async, it takes a lot of time for lot of repos ([`7b43c27`](https://github.com/RedHatInsights/vmaas/commit/7b43c27d0aac3574dc123fd3399d91dbab722f8a))

* add package tree generation and download to reposcan ([`d6cea1d`](https://github.com/RedHatInsights/vmaas/commit/d6cea1d0d517b9a7dc756b89f4be804a4e510e02))

* try to find releasever and basearch in url if not defined ([`be36b1f`](https://github.com/RedHatInsights/vmaas/commit/be36b1fa3c2faca3456a2d207a0e87f42cbf73bb))

* basearch and releasever can be None, return empty string in result ([`ede0a21`](https://github.com/RedHatInsights/vmaas/commit/ede0a2107b486a38918be870507d6f5be93c6163))

* reposcan can occasionally take more memory and crash silently - workaround ([`e62a18c`](https://github.com/RedHatInsights/vmaas/commit/e62a18c449fce25c2478e412f6d1d1a444bf72ac))

* support specifying custom app_id ([`93317e6`](https://github.com/RedHatInsights/vmaas/commit/93317e68bc53741c01d5318eac4b5647a7824522))

* fix SQL error when one of package or errata list is empty ([`fbf91ee`](https://github.com/RedHatInsights/vmaas/commit/fbf91eee08047eef8a81842ee1110d2251cab506))

* webapp: add possibility to turn off hot-cache via environment variable. ([`7f1ddcc`](https://github.com/RedHatInsights/vmaas/commit/7f1ddcc551f13865b68c79fe0a7f85196cd0cac5))

* reposcan: log successful requests to management API ([`dc12cd0`](https://github.com/RedHatInsights/vmaas/commit/dc12cd0d6ebddb35259bf6f580dbed73bbd96e7e))

* read reposcan host from env variable for rsync ([`df01d9e`](https://github.com/RedHatInsights/vmaas/commit/df01d9e630497b1e87ed9ebc0ab9b5da8e429525))

## v0.6.0 (2018-08-01)

### Unknown

* define requirements for services ([`ab8a2fc`](https://github.com/RedHatInsights/vmaas/commit/ab8a2fc106db6718f7fe8c9016fe819e3d9a3007))

* reposcan: add more logging for the failed authorization attempt. ([`c0dc8b9`](https://github.com/RedHatInsights/vmaas/commit/c0dc8b9516d2980b84428ebfa6f757998ae92fa9))

* reposcan: introduce authentication for the management API. ([`339ed28`](https://github.com/RedHatInsights/vmaas/commit/339ed28af5a13daa6c87d263d54f08ff58bfb2c9))

* Fix #371 - each log-call is a single line/entry

Extracted logging-code from webapp/utils.py into logging_utils.py
Added OneLineFormatter to logging_utils
Made reposcan/common/logging.py and webapp/logging_utils.py the same code ([`fd5be5b`](https://github.com/RedHatInsights/vmaas/commit/fd5be5ba6a6cb62363132bcf901f56181504aa66))

* Add v2 updates API that no longer returns package summary and description ([`50c9122`](https://github.com/RedHatInsights/vmaas/commit/50c91221decee7aa42f6a69e5bde76bfc6d18fd6))

* delete only old objects and keep current or delete all objects ([`1026751`](https://github.com/RedHatInsights/vmaas/commit/10267515f04334596ebe0b3630a0b5aec33fd702))

* point routes to the new deployment ([`9493c24`](https://github.com/RedHatInsights/vmaas/commit/9493c24bdf39c3157ae406d88b0419fd14ff77c8))

* add upgrade-start task ([`cd99fed`](https://github.com/RedHatInsights/vmaas/commit/cd99fed7602baaf0bcfb10c5dc4348e02ca0f193))

* set commit id to all components ([`0a552be`](https://github.com/RedHatInsights/vmaas/commit/0a552be684bf2dc618eaa44f4ffc29d124c6a156))

* Add packages API ([`d92df99`](https://github.com/RedHatInsights/vmaas/commit/d92df99f276b916749f457ccb06c89f97c3e3e6b))

* fix #365 - when repository basearch is null, repo is missing in dump ([`a0e06f0`](https://github.com/RedHatInsights/vmaas/commit/a0e06f0391ddc79f047283a2482c9d5704f89ef4))

* fix #333 - Make &#39;hot cache&#39; more tuneable via environment variables. ([`ef4beb0`](https://github.com/RedHatInsights/vmaas/commit/ef4beb0cefb7723a0468bd75d51cd54eb245f79f))

* webapp: use clear() method from Cache() constructor to avoid duplication. ([`e026fd8`](https://github.com/RedHatInsights/vmaas/commit/e026fd81b24db4e0b54ecf8e9fa2f42b90c1638f))

* Fix #360 - pylint ([`ce3463f`](https://github.com/RedHatInsights/vmaas/commit/ce3463fbc9937732f5a6d160de90b633d92bda2a))

* Fix #360 - update cve-api-spec definition w/new fields ([`a8aa87d`](https://github.com/RedHatInsights/vmaas/commit/a8aa87d1015ccbb93fe08c3d5b5deae83e31668d))

* Fix#360 - Teach /cve to include pkg and errata lists
 * Add cve-to-pid and cve-to-eid maps to exporter
 * Make pkgid2name a utils fn
 * Teach /cve to return errata-list and package-list as part
   of cve-details-json

This is an additive change - doesn&#39;t (shouldn&#39;t?) break /v1 callers. ([`d9700fd`](https://github.com/RedHatInsights/vmaas/commit/d9700fdf08be95b7792318b7b3dd019bd5adb6c4))

* fix issues detected by new pylint

invalid-envvar-default
no-else-return
consider-using-set-comprehension
useless-object-inheritance ([`d9e966b`](https://github.com/RedHatInsights/vmaas/commit/d9e966bd1c1f04071c8e6f9d0d040ac61c84edcd))

* swagger ui is also sending options request with parameter ([`e83564a`](https://github.com/RedHatInsights/vmaas/commit/e83564a816d08ddf3249ef764ac2527e95c4cd81))

* add missing parameter to apidoc ([`771dfe5`](https://github.com/RedHatInsights/vmaas/commit/771dfe50107d0cf262609f2d9847e1513dfdc7c9))

* return currently running task type ([`ecde604`](https://github.com/RedHatInsights/vmaas/commit/ecde60439d33ea83af4dbced409cab10fbb03e0f))

* fix &#39;TypeError: NetworkError when attempting to fetch resource.&#39; when API is called from swagger ui ([`4786dc6`](https://github.com/RedHatInsights/vmaas/commit/4786dc6886cbb0e63c75f6c4a6d66dbb879c15de))

* fix pylint ([`9870126`](https://github.com/RedHatInsights/vmaas/commit/98701262dbcab801f4405fa05f024bea41a59d25))

* support canceling currently running background task ([`2e674b5`](https://github.com/RedHatInsights/vmaas/commit/2e674b5adde940ed161a9e74b68dacf642108bf7))

* delete unassociated packages/errata after repository sync/deletion ([`425a629`](https://github.com/RedHatInsights/vmaas/commit/425a629dd248a5c5e393d7a2ee129f96c44ea1d2))

* implement DELETE of repositories ([`f53a548`](https://github.com/RedHatInsights/vmaas/commit/f53a5482926cca033b12e78491253d1fff107d2e))

* fix import of content sets with empty basearch or releasever list ([`875a5a8`](https://github.com/RedHatInsights/vmaas/commit/875a5a8b1dc0da0951011ef02441f3816df86f69))

* run ExporterHandler after each sync task better way ([`4d0ee78`](https://github.com/RedHatInsights/vmaas/commit/4d0ee7809dbc16664048fd39d438afb3b43019d1))

* remove monitoring category from apidoc ([`c117fce`](https://github.com/RedHatInsights/vmaas/commit/c117fcebba199aa39ea17acf0e869da171623790))

* change GET to PUT for sync and export APIs ([`09bbe20`](https://github.com/RedHatInsights/vmaas/commit/09bbe20f9214dc633650a5b14742d8bff6e46a36))

* make revision nullable to import repository records before actual sync ([`d74ce6c`](https://github.com/RedHatInsights/vmaas/commit/d74ce6c22ac9f5d80b297d293fc992b84f36d813))

* move importing product/repo definitions from JSON to the new handler ([`5b19597`](https://github.com/RedHatInsights/vmaas/commit/5b19597757eb90305f732b77d47bb5c57ec7ef86))

* define new /api/v1/repos* handlers ([`1bba4d1`](https://github.com/RedHatInsights/vmaas/commit/1bba4d1343f3d13809bc1695c536229a151165bb))

* rename API handler: /api/v1/sync/export -&gt; /api/v1/export ([`3b4ad80`](https://github.com/RedHatInsights/vmaas/commit/3b4ad80a0c854bf4556f978cfa366ae3f161f83e))

* fix #355 - disable dropdown list with fixed schema in apidoc ([`f0912ce`](https://github.com/RedHatInsights/vmaas/commit/f0912ce0f372248a52e14168eaec0b1fe003b6a6))

* fix #355 - webapp and reposcan APIs are on https ([`a0728b2`](https://github.com/RedHatInsights/vmaas/commit/a0728b27df67ce2163575e8f33464023355fc260))

* fix #355 - create secured routes ([`31101a2`](https://github.com/RedHatInsights/vmaas/commit/31101a2626c8028a190473e4adb7c8ff9b3fbcdc))

* The &#39;M&#39; stands for &#39;Metadata&#39; ([`14275ac`](https://github.com/RedHatInsights/vmaas/commit/14275acfd3dc644abd5ae2d808e859685aeafbb5))

* in case of traceback log complete input data ([`3443fdd`](https://github.com/RedHatInsights/vmaas/commit/3443fdd69f51b994277b4d1cdae807c985538437))

* log data version after cache (re)load ([`d2a51a2`](https://github.com/RedHatInsights/vmaas/commit/d2a51a2a281e3674285147f0e856348e3f4a4ed9))

* change logging_type for released versions ([`21bb48e`](https://github.com/RedHatInsights/vmaas/commit/21bb48ef7d25d714e3bf5a22b58abbfbab9b3c16))

* define env variable only in one place ([`89409e3`](https://github.com/RedHatInsights/vmaas/commit/89409e35c74e33779c31aec87a48fabe12a61626))

* in openshift do not log container id and time

it&#39;s already handled/added by kibana
moreover it confuses default filtering ([`4ab1f88`](https://github.com/RedHatInsights/vmaas/commit/4ab1f884281c9ffb58ae53ae29168a2a63b65494))

* set default logging_level for webapp ([`371be73`](https://github.com/RedHatInsights/vmaas/commit/371be7388e862c2bef1ec0122bdcd0bdd133beda))

* fix #350 - compare &#39;date of publication&#39; only if &#39;date of modification&#39; is not set. ([`fc87e14`](https://github.com/RedHatInsights/vmaas/commit/fc87e148ce9634b94432015d7af1c94e38b58019))

* fix #239 - example is not allowed for non-body request in OpenAPI 2.0 ([`9e697e5`](https://github.com/RedHatInsights/vmaas/commit/9e697e5955acc423d786fbd23cf92d1b99553c6f))

* change warning -&gt; info ([`c2d8856`](https://github.com/RedHatInsights/vmaas/commit/c2d8856fae3cc5d8cab32974b8fba444f42373f3))

* fix #334 - in case of ISE log whole traceback ([`88db6f7`](https://github.com/RedHatInsights/vmaas/commit/88db6f701b65f4df42d73f841160f1b4dd374c07))

* fix #334 - include vmaas version in log ([`c436391`](https://github.com/RedHatInsights/vmaas/commit/c43639183330f50a778eb3469cc8787ee54c4068))

* fix #334 - added logging into webapp ([`21e4d7f`](https://github.com/RedHatInsights/vmaas/commit/21e4d7fc4ca21117eaf4434a9650bcae15e057ba))

* fix #334 - added container id to reposcan logs ([`4aceb1a`](https://github.com/RedHatInsights/vmaas/commit/4aceb1ad2359f6983b947801a11d0d2a995d4fe3))

* fix #344: compare only non-empty dates with &#39;modified_since&#39;. ([`fe73b03`](https://github.com/RedHatInsights/vmaas/commit/fe73b03fa93926aa241f4a93f02661d3f1124a21))

* fix #345 - NameError: name &#39;ExporterHandler&#39; is not defined ([`1127e4d`](https://github.com/RedHatInsights/vmaas/commit/1127e4da630c11809c67ddfb4a80d8da872ac29a))

* fix #345 - do not run export in callback, it&#39;s a blocking operation, callback should finish ASAP ([`31fcec4`](https://github.com/RedHatInsights/vmaas/commit/31fcec4329598d0ccf72b562599e07da7bd899fd))

* fix #343 - add handling of malformed regular expressions for GET methods ([`f36a66a`](https://github.com/RedHatInsights/vmaas/commit/f36a66aff2dc36aa7d5b2cb78566408843874c44))

* extract duplicated code into super class ([`71a5d31`](https://github.com/RedHatInsights/vmaas/commit/71a5d31c1c044fdb76b1a2a4becb56fb9913538c))

* fix #343 - add handling of malformed regular expressions for POST methods ([`f26ea9b`](https://github.com/RedHatInsights/vmaas/commit/f26ea9b4d5b29b6063d36a2f2956258401c5f2fa))

* set version of the application when creating new release ([`05efbbb`](https://github.com/RedHatInsights/vmaas/commit/05efbbb1bfd1b4ad73f273ba5ca35709bd667ea0))

* add API returning version of the application ([`7323e47`](https://github.com/RedHatInsights/vmaas/commit/7323e47779e1eb193b5f7defa2fc658bd89d5abb))

* display version of the application in apidoc ([`83779bd`](https://github.com/RedHatInsights/vmaas/commit/83779bd857b69fe843946ff89e58431ed7a7815e))

* updates: pylint fix - shadows built-in &#39;id&#39; name. ([`fbf0f6b`](https://github.com/RedHatInsights/vmaas/commit/fbf0f6b827b5e171b065e06c6c7b2e27dd3574c4))

* extract duplicated code into super class ([`50c6470`](https://github.com/RedHatInsights/vmaas/commit/50c6470cca0bc97b42f596b4ac9feab14f2f0ed0))

* add apidoc healthchecks ([`57537d6`](https://github.com/RedHatInsights/vmaas/commit/57537d613fc93c18f313f2b8f596b826a205ca7c))

* add postgresql healthchecks from official template ([`646e043`](https://github.com/RedHatInsights/vmaas/commit/646e043bf1b2927dd7da69310ef2ae3d51843820))

* add reposcan healthchecks ([`9597e97`](https://github.com/RedHatInsights/vmaas/commit/9597e9790f8c062ffc9591226f6e519955d41270))

* run single webapp server per container by default

in OpenShift healthchecks are per container, it doesn&#39;t work if there is another scaling mechanism enabled in application - how to detect if only half of the app is broken? ([`7b767e9`](https://github.com/RedHatInsights/vmaas/commit/7b767e9a5ea882bd6c4643e1b51107252b9ee395))

* add webapp healthchecks ([`4fda223`](https://github.com/RedHatInsights/vmaas/commit/4fda223d4452207f3f634704b063da91fd34d5d6))

* add simple reposcan status API ([`bb65991`](https://github.com/RedHatInsights/vmaas/commit/bb6599197256dd48ade933024dd2c196f699503a))

* add simple webapp status API ([`358510e`](https://github.com/RedHatInsights/vmaas/commit/358510ee1854eebc538dc1a9774274fbdd41743f))

* fix #329 - add JSON validation to other handlers ([`ec0a687`](https://github.com/RedHatInsights/vmaas/commit/ec0a6878de91ebcd0ab257c5e18386504fbe4d2b))

* fix #335 - add pagination to /repos API ([`c0e892d`](https://github.com/RedHatInsights/vmaas/commit/c0e892d0d73aae20857aedc152eae4c924512e35))

* fix #327 - execute selects only if there are any errata_ids ([`60868c0`](https://github.com/RedHatInsights/vmaas/commit/60868c06f46bfa898139ddb42a427eb6b6b6b49c))

* Fix #312 - teach cvemap that &#39;red hat wins&#39; only if RH has something to say ([`4434ffa`](https://github.com/RedHatInsights/vmaas/commit/4434ffa2d154508a9d4b763ef1149f6ff0b15d20))

* fix #326 - check anchors during regex processing ([`5dae30c`](https://github.com/RedHatInsights/vmaas/commit/5dae30c5da257aa69d0a677a1fda3496bd300d2d))

* fix #310 - don&#39;t export non-security errata details ([`6c86d4d`](https://github.com/RedHatInsights/vmaas/commit/6c86d4d3fbf13803cb7b2a26f7d74a3ab15d6347))

* start application from the same directory as entrypoint.sh

so you can (re)use it to start app in development setup ([`b5e79ef`](https://github.com/RedHatInsights/vmaas/commit/b5e79efa4cbf865e4d8142ae9f519f5e604774cb))

## v0.5.0 (2018-06-20)

### Unknown

* fix #320 - don&#39;t convert None into string, just return None

when format_datetime received None it converted into string &#34;None&#34;
which was confusing for subsequent calls with returned value
which were doing tests for None as &#34;None&#34; is None == False ([`6658461`](https://github.com/RedHatInsights/vmaas/commit/6658461681c32649b08bfc5c89a4f5b1b6db2fc8))

* fix typo ([`faf9900`](https://github.com/RedHatInsights/vmaas/commit/faf99005b4ed6014a6a44b1d3c16bd6ea653095e))

* remove database dependency from webapp ([`863f6fc`](https://github.com/RedHatInsights/vmaas/commit/863f6fce17fb2d470170a2ff880d120ff6d36faf))

* fix #316 - skip non-existent repository ([`b128c2a`](https://github.com/RedHatInsights/vmaas/commit/b128c2ab9c26596d7a6b26381e9b305e752684ce))

* fix #317 - use IOLoop from main thread in callback ([`7b24d3e`](https://github.com/RedHatInsights/vmaas/commit/7b24d3ea7f5dda526a5f8103955c8772c570f655))

* copy the data behind the symlink not link itself ([`b856126`](https://github.com/RedHatInsights/vmaas/commit/b8561260008dd19cece2554267a4b121e6a5b1f3))

* symlink doesn&#39;t exist (yet) during the first export ([`06f3e9e`](https://github.com/RedHatInsights/vmaas/commit/06f3e9ee22f88f1fcdf5d38b4a5fd76e37ea15a6))

* fix #311 - check anchors during regex processing. ([`d80ed1f`](https://github.com/RedHatInsights/vmaas/commit/d80ed1f59d80637cef31b9f1a1a6eb1802639e90))

* keep several version of data on disk ([`3111489`](https://github.com/RedHatInsights/vmaas/commit/311148948417f8b9561ee888173d211a811973d1))

* fix #299 - skip unknown repositories ([`bf6af34`](https://github.com/RedHatInsights/vmaas/commit/bf6af34fc421a7e7a386c1cc06d671d4b99f9bc0))

* fix #299 - require timezone in timestamps ([`aa42c6f`](https://github.com/RedHatInsights/vmaas/commit/aa42c6f29056d0dda9de649d9477dc28efb69b71))

* issue #306 api: updates: before put response into cache, we should take into account what repos were passed in the input JSON. ([`f8849a9`](https://github.com/RedHatInsights/vmaas/commit/f8849a96da8afd710e4407acfa20cc3652cdef9a))

* api: updates: rename cache to db_cache, since we have two types of caches now. ([`0e6f418`](https://github.com/RedHatInsights/vmaas/commit/0e6f418439d7367f82d740c50ef8d438bfd7c67b))

* #301 api: updates: if all packages are in the hot cache already, we need to fill a response with the input repo information anyway. ([`f884dfc`](https://github.com/RedHatInsights/vmaas/commit/f884dfc75215338e69920430af0cd12bfd5edc1a))

* updated /errata to use pagination ([`67cb843`](https://github.com/RedHatInsights/vmaas/commit/67cb843a17269ac8ca96197773be6e23e0d39f9e))

* Make errata api use Phase II design ([`725443a`](https://github.com/RedHatInsights/vmaas/commit/725443a069954142f07d2393f89e331cb4e82206))

* api: updates: add multi-level cache.

Implementation is based on Splay Tree, see https://en.wikipedia.org/wiki/Splay_tree ([`dc783bf`](https://github.com/RedHatInsights/vmaas/commit/dc783bf41831461560d7f3ac77bb8d88c04631ad))

* fix #296 - removed unused method ([`30d1749`](https://github.com/RedHatInsights/vmaas/commit/30d174943571737831a99275ee32f9573338061f))

* modified /dbchange to use disk dump ([`39255d7`](https://github.com/RedHatInsights/vmaas/commit/39255d7c867057183668d48670e9529bd8779cfe))

* introduced pagination for /cve API ([`f1529ab`](https://github.com/RedHatInsights/vmaas/commit/f1529abe783e30d68c509bb364d2b898bd865d05))

* Fix #273 - pylint ([`d9d1553`](https://github.com/RedHatInsights/vmaas/commit/d9d1553ae9ba711b8ee60a6d3fd0afb7434cf1b5))

* Fix #273 - Build updates-response per-erratum instead of per-repo

A single package nevra can be released into different repositories
by different errata. When looping by repositories, we confused this
issue, resulting in being able to show erratum for repositories they
didn&#39;t belong to.

Swicthed the loop-nesting, so that we now build /updates by-erratum,
instead of by-repository. ([`7a1d005`](https://github.com/RedHatInsights/vmaas/commit/7a1d0052d85c645fcbe438a5a04eb76fa82bc283))

* modified /cve API to use disk dump ([`6f24bac`](https://github.com/RedHatInsights/vmaas/commit/6f24bac98e7fa6d8a2703e3ef66ad22c547fc382))

* removed unused ListDict class ([`79b0b67`](https://github.com/RedHatInsights/vmaas/commit/79b0b673530467e28dd5ac3257d70b061298e9db))

* fix #280 - find correctly last item with given evr in updates list ([`acb6ddb`](https://github.com/RedHatInsights/vmaas/commit/acb6ddbc3bafe5d35ff16c8d0ed5d0029ad7b238))

* webapp: run several tornado.httpserver.HTTPServer instances.
This give us some performance boost. ([`44f4b7e`](https://github.com/RedHatInsights/vmaas/commit/44f4b7ef41246030fededa853bfd4ec363b0df35))

* fix empty database export ([`c0cd862`](https://github.com/RedHatInsights/vmaas/commit/c0cd86276d59e59d8974de952a8a2616ac5156d3))

* run exporter after each sync task automatically ([`949cc2f`](https://github.com/RedHatInsights/vmaas/commit/949cc2f43e086e8816e87b7c92ce18af34079f91))

* run as non-root user even in docker

openshift runs containers as non-root let&#39;s do the same in docker
to catch issues during development not deployment ;) ([`00d9538`](https://github.com/RedHatInsights/vmaas/commit/00d9538eaa89024b24242b8ff03aedd074e5fcba))

* Issue 120 - disable a few pylint checks in pylintrc to clean up disable comments in code ([`d8a3061`](https://github.com/RedHatInsights/vmaas/commit/d8a30614ae1b88ed8fd7ce154d89bd62311dc979))

* expose running rsync daemon port ([`c27853a`](https://github.com/RedHatInsights/vmaas/commit/c27853a33bb0b45058298e8b2217b9c3a4b99eda))

* #274 - CVE class wasn&#39;t threadsafe ([`7620e44`](https://github.com/RedHatInsights/vmaas/commit/7620e44b853bdba84d8b620a2e90a2a7d28e67f8))

* /data have to be writable for non-root users as well ([`8e29dd5`](https://github.com/RedHatInsights/vmaas/commit/8e29dd5068586afd6267cb5264529fb5fcf783f8))

* modify rsync to run in openshift

containers in openshift run as non-root so they can&#39;t open port &lt; 1024 ([`93e3cc5`](https://github.com/RedHatInsights/vmaas/commit/93e3cc57214448db4a902ee5f36aad99d11b1759))

* #263 close every DB connection since we don&#39;t have pool yet. ([`0c8c51c`](https://github.com/RedHatInsights/vmaas/commit/0c8c51cd933ea0d3100315b728c2f6aaeeabe020))

* wait until apidoc is deployed before changing configuration ([`d67a2a0`](https://github.com/RedHatInsights/vmaas/commit/d67a2a0c7bc664f4065ced0968df864c548bf1d4))

* improve script to do more setup tasks ([`4722b1d`](https://github.com/RedHatInsights/vmaas/commit/4722b1d921c620253ef2ce42fd58155652730964))

* remove disk size kompose params - not usable when there are multiple volumes in single service ([`7517b90`](https://github.com/RedHatInsights/vmaas/commit/7517b90fda3595a4023fd3abb6fc238c6ac23e78))

* continue with deletion when routes don&#39;t exist ([`db26562`](https://github.com/RedHatInsights/vmaas/commit/db2656268a455b7e62b0e1478c661493d5c6838d))

* enhance error handling to return meaningful error message to the caller ([`16bfc26`](https://github.com/RedHatInsights/vmaas/commit/16bfc26875fe8c5c426664475208f33c128be9bf))

* updated /repo to use disk dump cache ([`12a9bc8`](https://github.com/RedHatInsights/vmaas/commit/12a9bc8892565aeed900bd46931912f85def152f))

* sync data from reposcan via rsync ([`be12bc1`](https://github.com/RedHatInsights/vmaas/commit/be12bc13f1e2fba4928c19728eff634795c08732))

* setup rsync daemon on reposcan ([`10adead`](https://github.com/RedHatInsights/vmaas/commit/10adead9287cb4249c0265c38704925fd0432af6))

* define correct variable ([`9845ce6`](https://github.com/RedHatInsights/vmaas/commit/9845ce643e8351fb4a8bda3093b341cdb914a28f))

* filter does not return list in python3

fixing
Traceback (most recent call last):
...
  File &#34;/git/cve.py&#34;, line 68, in process_list
    if len(cves_to_process) == 1:
  TypeError: object of type &#39;filter&#39; has no len() ([`73b4f27`](https://github.com/RedHatInsights/vmaas/commit/73b4f27c5bca124d1429ccec0bbd8443a6d0a94c))

* updated images to latest Fedora ([`6935a0c`](https://github.com/RedHatInsights/vmaas/commit/6935a0c7268d94f26ab80d635b59af74388d7ad7))

* use python3 in webapp for compatibility with reposcan

fixing
Traceback (most recent call last):
...
  File &#34;/usr/lib64/python2.7/shelve.py&#34;, line 122, in __getitem__
    value = Unpickler(f).load()
ValueError: unsupported pickle protocol: 3 ([`f7f9d6a`](https://github.com/RedHatInsights/vmaas/commit/f7f9d6a2d3a1a07981dea19924e405abeacfd3aa))

* added shared data volume for file dumps ([`000b2ac`](https://github.com/RedHatInsights/vmaas/commit/000b2ac1adb3c77fd4990343dca3fd9a25b56e5d))

* modified UpdatesApi to read data from file dump ([`4e3a7a4`](https://github.com/RedHatInsights/vmaas/commit/4e3a7a4e4b29f01b41ff9fd5a4659486c0949251))

* initial version of exporter module ([`332b631`](https://github.com/RedHatInsights/vmaas/commit/332b6312f6f33f5ab40df44eb1aaa6a619d8babb))

* simplify use of named cursor

intended use is:
    with named_cursor(db_instance) as cur
        cur.execute(...) ([`18a825b`](https://github.com/RedHatInsights/vmaas/commit/18a825b23cada5bc76896c45df95797f04bafe85))

* move init_db() into database module ([`ddffdfc`](https://github.com/RedHatInsights/vmaas/commit/ddffdfc68c86d06c6b8d1a348eaba4d85e6b2878))

* workaround broken yum/copr plug-in on el7

Error: [Errno 14] HTTPS Error 404 - Not Found
ERROR: Service &#39;webapp&#39; failed to build: The command &#39;/bin/sh -c yum -y update     &amp;&amp; yum -y install yum-plugin-copr     &amp;&amp; yum -y copr enable @vmaas/libs     &amp;&amp; yum -y install epel-release     &amp;&amp; yum -y install python-tornado python-psycopg2 python2-apispec postgresql python-dateutil python2-futures python2-jsonschema     &amp;&amp; rm -rf /var/cache/yum/*&#39; returned a non-zero code: 1 ([`f890db3`](https://github.com/RedHatInsights/vmaas/commit/f890db307cba109e85075f92eba856ac5da95e48))

* rewrite /updates API to use cached data only ([`eeb1e36`](https://github.com/RedHatInsights/vmaas/commit/eeb1e3607c995ecf666b39fcf404c7834aea7be3))

## v0.4.0 (2018-05-17)

### Unknown

* Make updates api db query more efficient ([`0ab58c9`](https://github.com/RedHatInsights/vmaas/commit/0ab58c9465b3e1ebae3aad93b414f45033476cf8))

* do not re-create cache with every request ([`fb9637e`](https://github.com/RedHatInsights/vmaas/commit/fb9637e85b55b1759cdeb3fb39a034161c74360e))

* Fix #252 - validate incoming /updates json, using jsonschema
Also adjust existing ValueError to return more useful error-info ([`a78ad46`](https://github.com/RedHatInsights/vmaas/commit/a78ad46ce3e1a48ffb15dec7008e552b328e3775))

* ask user if selected Git branch and OpenShift environment is correct before deployment ([`4a2442f`](https://github.com/RedHatInsights/vmaas/commit/4a2442fe4bedc42f9cbb535ad855f3cc32b2ec99))

* api: webapp: POST request always should be asynchronous, even when it doesn&#39;t return Future object. ([`5e36c92`](https://github.com/RedHatInsights/vmaas/commit/5e36c92688359435fcfe8d5b7b21f77546a28bcc))

* cancel any already running rollout before triggering new one ([`02c92e9`](https://github.com/RedHatInsights/vmaas/commit/02c92e9cd03c0224a24d609371c59bedea684a57))

* api: webapp: add abbility to process request in parallel.

Run the blocking code (every request to the Database) on another thread using concurrent.futures.ThreadPoolExecutor.

All tornado methods (like write(), flush()) can only be safely called from the IOLoop thread. ([`b8f092d`](https://github.com/RedHatInsights/vmaas/commit/b8f092d5e432f445052cb77b693f9dc5954af099))

* api: webapp: install python2-futures from EPEL in the webapp container. ([`f2153c3`](https://github.com/RedHatInsights/vmaas/commit/f2153c3164f5886129ab243f9937257591823f62))

* Fix #251 - Teach cvemap that Red Hat data always wins ([`00b961a`](https://github.com/RedHatInsights/vmaas/commit/00b961acd50d139d46a42184d4210c2f1b7179d1))

* fix #248 - wait until reposcan API is available ([`5f82ea5`](https://github.com/RedHatInsights/vmaas/commit/5f82ea567d94f074fa089f024dbe243dec53eedc))

* fix #248 - setup websocket client on webapp ([`8e94287`](https://github.com/RedHatInsights/vmaas/commit/8e942872adfba3e2657f8d3b308d79533cb62a14))

* fix #248 - manage active clients on server side ([`003a22a`](https://github.com/RedHatInsights/vmaas/commit/003a22a6035260269e303726e77ebbed028bb635))

* fix #248 - setup websocket handler ([`a80cbed`](https://github.com/RedHatInsights/vmaas/commit/a80cbede09f0b161229b01856d38bbd726c792d9))

* Fix #223 - default reposcan-postgresql-pwd correctly ([`159c38f`](https://github.com/RedHatInsights/vmaas/commit/159c38f1373cd8388afcf020553f24613da3b919))

* Fix #223 - Teach reposcan.py to default to vmaas_writer if no pgres-user ([`8069597`](https://github.com/RedHatInsights/vmaas/commit/80695979e3ecaf1796d693f80fb05a13910d2978))

* Fix #223 - Fixed a misunderstanding of how Dockerfile, docker-compose,
and config-files interact ([`4e8e41c`](https://github.com/RedHatInsights/vmaas/commit/4e8e41caaed74eb8e574e537247c899fa8203caf))

* Fix #223 - Add limited users to different components
- vmaas_admin is used by database to create vmaas DDL
- vmaas_writer is used by reposcan to insert/update/delete DML
- vmaas_reader has select-only access to tables, used by webapp

Notes:
* Currently we create everything into &#39;public&#39; schema; may want to have
a specific &#39;vmaas&#39; schema.

* CREATE USER has to run as the postgres user initially; hence the
database/vmaas_user_create_postgresql.sql being run in database/init_schema.sh ([`7fd69fd`](https://github.com/RedHatInsights/vmaas/commit/7fd69fdc132a5634b79bfa46c3f0fa249017b2db))

* added redhat&#39;s cvemap import ([`81883db`](https://github.com/RedHatInsights/vmaas/commit/81883db192f01792db565f66d0de6546a44bf8c8))

* splitted CveStore into two classes

so I can reuse some code ([`c404e5a`](https://github.com/RedHatInsights/vmaas/commit/c404e5a354a91190cc4fc7ea465b63b8296a42d1))

* insert source of CVE into database

and update cve only if it came from the same source ([`e2e4466`](https://github.com/RedHatInsights/vmaas/commit/e2e44660a0d1c1f958aac6d81e685b93b3046447))

* remember where cve detail comes from ([`e65e647`](https://github.com/RedHatInsights/vmaas/commit/e65e647ae6b3338be560d431bd7488a2e8e5245b))

* modified strip() to check also for element != None ([`79334e2`](https://github.com/RedHatInsights/vmaas/commit/79334e2e28b9b48932bdf6c3b913bc5689034f06))

* extend FileDownloader to be able use HEAD method ([`c9cf7c9`](https://github.com/RedHatInsights/vmaas/commit/c9cf7c9779523a5af2a9596777adaab4abadcace))

* fix #190 - add tasks to configure OpenShift endpoints in apidoc automatically ([`a478420`](https://github.com/RedHatInsights/vmaas/commit/a478420c32b181e54a6e973adda33b0f0d2a07ed))

* fix #190 - add tasks to create and delete routes ([`b36bbbc`](https://github.com/RedHatInsights/vmaas/commit/b36bbbc1171a0eeb794c1d0cfba4839e95036e87))

* api: cli-tool: print error message if input JSON is malformed. ([`c4efa55`](https://github.com/RedHatInsights/vmaas/commit/c4efa558e850edd21e32ee79c9db6a364e37aba3))

* fixing long line and reducing number of vars in method ([`d03b36d`](https://github.com/RedHatInsights/vmaas/commit/d03b36d0bc6df2dd8379ebe35f14d46b67cf5306))

* update webapp to use package_name table ([`3712bcb`](https://github.com/RedHatInsights/vmaas/commit/3712bcb2fd9c7b4eaee026edc6ca20e2a2f487d4))

* populate package_name table and refactor package import class for better performance ([`fa7cf23`](https://github.com/RedHatInsights/vmaas/commit/fa7cf23143200cf2286ccffede962b1ba1681510))

* store package names in new package_name table and add indexes for better performance ([`f2f221e`](https://github.com/RedHatInsights/vmaas/commit/f2f221ef7412699c0e056eed2f8a841440e2de30))

* fix #242: add possibility to pass regex in a URL without percent-encoding. ([`f588730`](https://github.com/RedHatInsights/vmaas/commit/f58873030a4c07efd42cc4a7f9c5766d231db705))

* fix #241 - Fix typo in &#39;releasever&#39;. ([`12bf912`](https://github.com/RedHatInsights/vmaas/commit/12bf912f6218dc4347cb7c1bcf0dd465dfe3bc2b))

* Fix #237 - pattern-name used in route is a &#39;magic string&#39; to apidoc ([`befaa7c`](https://github.com/RedHatInsights/vmaas/commit/befaa7cfdfed6eed4d6798af2450a6beb6e486cb))

* increase disk size requirements for reposync tmp cache and persistent database ([`b088350`](https://github.com/RedHatInsights/vmaas/commit/b0883507c55e70e387845d1f1745c066548809b3))

* Add regex support to errata api. ([`fb07a91`](https://github.com/RedHatInsights/vmaas/commit/fb07a910f36d25283356c7eed0b23348771acfa0))

* add wrapper strip function considering None for .text XML attributes ([`1eed5ac`](https://github.com/RedHatInsights/vmaas/commit/1eed5acc6948f5eee18f28ebc9f90173cfd85b77))

* catch failed downloads when downloading metadata ([`c6c3221`](https://github.com/RedHatInsights/vmaas/commit/c6c322104365f3ba4e0c64b265d94ecd6b23bf4c))

* keep evr_map in memory ([`a7f49b7`](https://github.com/RedHatInsights/vmaas/commit/a7f49b7e650b4dab02c6229b4fe1896bd322c681))

* add indexes for second columns in mapping tables to improve performance ([`46fb57c`](https://github.com/RedHatInsights/vmaas/commit/46fb57cd2509378aa3d00021f4aa28c033f24154))

* retry download in case of ProtocolError ([`ea1fb36`](https://github.com/RedHatInsights/vmaas/commit/ea1fb36131ad7157f0e0e5212d36ccd2aa025c62))

* Fix too-long-line in apispec strings ([`202d532`](https://github.com/RedHatInsights/vmaas/commit/202d532fe179deee05c857d37b1c5de406e466e4))

* Extended /repos to allow POSIX regex in GET or POST to return multiple repositories
Also fixed &#39;cve GET&#39; APISpec to allow it to work from apispec page ([`c2e5e25`](https://github.com/RedHatInsights/vmaas/commit/c2e5e2514b2b355636c60c52cfe334267f8a6044))

* Fix #217 - don&#39;t dump traceback when attempting to notify webapp ([`35bf2b6`](https://github.com/RedHatInsights/vmaas/commit/35bf2b60333f92e159eccfd5f844089304b66bc1))

* Fix #217 - add error handling to avoid tracebacks in the logs. ([`540e411`](https://github.com/RedHatInsights/vmaas/commit/540e41194128a964ea2eefee930ad8833ef0a6b0))

* *SyncHandler classes have to be defined before SyncTask

fixing
NameError: name &#39;RepoSyncHandler.run_task&#39; is not defined ([`17a933b`](https://github.com/RedHatInsights/vmaas/commit/17a933b33a9e1eba590624a794ce91245822c646))

* move all_sync_task into AllSyncHandler class ([`e411a59`](https://github.com/RedHatInsights/vmaas/commit/e411a59cf67cc0095a0907888b2da58fb7af39e1))

* move cve_sync_task into CveSyncHandler class ([`3cfeecd`](https://github.com/RedHatInsights/vmaas/commit/3cfeecd92882b99009a51414031a091ae26b4013))

* move repo_sync_task into RepoSyncHandler class ([`2000522`](https://github.com/RedHatInsights/vmaas/commit/200052237f0e876e6bc40241f37a9bb129a21f57))

* make extra params of start_task() optional ([`84695f8`](https://github.com/RedHatInsights/vmaas/commit/84695f8a2003a7d266bb8a312324e429c75a4373))

* use finish_task() method directly instead of task_callback parameter ([`469f5ad`](https://github.com/RedHatInsights/vmaas/commit/469f5ad6009e2c6cf081c53576a93159c824c697))

* make task_type class attribute

so we don&#39;t have to pass it as a parameter ([`773547e`](https://github.com/RedHatInsights/vmaas/commit/773547ef82cd38256e20853a498764b14a39d923))

* enable NIST cve data url override

mainly usefull for testing ([`cc320cd`](https://github.com/RedHatInsights/vmaas/commit/cc320cda37c5af2fbe7518a5cbe0ffc85c2e368a))

* Fix #207 api: cves: fix docs string according to the ability to pass regex, update GET handler to suport regex. ([`2e7952e`](https://github.com/RedHatInsights/vmaas/commit/2e7952e4baa650700d9aa3cb0d69b6cf6e6c897f))

* Fix #207 api: cves: add ability to get all CVEs by regular expression. ([`22306c0`](https://github.com/RedHatInsights/vmaas/commit/22306c041d621fc25eab681698fb69ab8f79e94e))

* pylint is a harsh mistress ([`74b39a4`](https://github.com/RedHatInsights/vmaas/commit/74b39a457217f14f5ff0024021f7750deb0d7aee))

* Add API to return last DB change

- Adds &#39;dbchange&#39; table to schema to track errata/cve/repos/any most-recent-change
- Adds initial-insert to guarantee dbcnage starts out with &#39;time db was created&#39;
- Adds functions to db to update the columns in dbchange
- Adds triggers to various tables to call the appropriate function, depending on
  which entity is changed
- adds webapp/dbchange.py to expose the API /api/v1/dbchange
- adds APISpec doc for same ([`392e005`](https://github.com/RedHatInsights/vmaas/commit/392e005a470f2881c47131c6d75d7dbe11153715))

* add script for listing RH repositories and generating request JSON for reposcan ([`90d0990`](https://github.com/RedHatInsights/vmaas/commit/90d0990cc06a65c8f835797b68386081eb7a570f))

* make sure errata pkglist is unique to not crash in case of error in repodata ([`a7a3a73`](https://github.com/RedHatInsights/vmaas/commit/a7a3a7322aec5497b45656440fa26838ac1dc8e8))

* epoch may be missing, set default to 0

e.g. /content/dist/rhel/server/6/6.6/x86_64/rh-common/debug ([`b94c250`](https://github.com/RedHatInsights/vmaas/commit/b94c2506ac905d4482c223cb625dfdf31a7a2e60))

* pkglist may be missing

e.g. /content/dist/rhel/server/6/6.6/i386/rh-common/debug ([`f4de50b`](https://github.com/RedHatInsights/vmaas/commit/f4de50bb9b97086b10358dbe734ddb397bb70b80))

* fix case when XML node is empty - None is returned and do strip once ([`8e2ba1d`](https://github.com/RedHatInsights/vmaas/commit/8e2ba1db9e1e0d9420d2af96ea4d5ff4ad1bd219))

* let revision be 0 if not found in repodata ([`ec69f6f`](https://github.com/RedHatInsights/vmaas/commit/ec69f6fbe05c3804c64e795f2709aaeab501b2af))

* omit size field, it&#39;s not used and repos may not containt it

e.g. /content/dist/rhel/workstation/5/5.7/i386/desktop/os/ ([`6d07cf9`](https://github.com/RedHatInsights/vmaas/commit/6d07cf908503b655b79515941f2c49cf78d4960f))

* Fix #221 - use explicit ids on keyword tables and add NotSet to cve impact ([`1548385`](https://github.com/RedHatInsights/vmaas/commit/1548385d2daff84a611a8aaa22a93887c502efca))

* vmaas cli: CveAPI doesn&#39;t require repocache.
TypeError: __init__() takes exactly 2 arguments (3 given) ([`4e06d5f`](https://github.com/RedHatInsights/vmaas/commit/4e06d5fdc87cdbee76aed2c513af975386de4d55))

* vmaas cli: add DB error handling, print errors to STDERR instead of standard output stream. ([`769f748`](https://github.com/RedHatInsights/vmaas/commit/769f74886adb41e5886bfa2507e6cd66aa28cbf9))

* Fix #206 - get impact from baseMetricV2 if V3 doesn&#39;t exist ([`bbd32d2`](https://github.com/RedHatInsights/vmaas/commit/bbd32d296cf0028ad841507e3b2a8ca8f787d6c6))

* pylint fixes ([`d607d0f`](https://github.com/RedHatInsights/vmaas/commit/d607d0fa21847268847c1b09f09608c93287437d))

* Fixes Issue #147 by using statically defined key tables for severity and impact ([`fe412fe`](https://github.com/RedHatInsights/vmaas/commit/fe412fe0e235d1ba4492baa0c3d2517e4812e0d5))

* Fix #23 - Missed changing DEFAULT_BATCH_SIZE to BATCH_SIZE in env ([`30e699b`](https://github.com/RedHatInsights/vmaas/commit/30e699b837721ca8a6fa3bd380b3ec04d7679dcd))

* Fix #23 - make some hardcoded values tuneable via env ([`d3dc27c`](https://github.com/RedHatInsights/vmaas/commit/d3dc27c9a1b1d8c52757fbf48ca909c638ef6bab))

* Fix #209 - Check published as well as modified, if modified-since is present

NOTE: this still interprets &#34;no date&#34; as &#34;never changed&#34;; if both fields are
null, the CVE continues to be filtered out by modified-since ([`cdd8122`](https://github.com/RedHatInsights/vmaas/commit/cdd8122d7599bb61769ec97b6cd759e5a5d91e99))

* fix #208 - use description and summary from correct nevra ([`b4e9169`](https://github.com/RedHatInsights/vmaas/commit/b4e91696eb5540c3c582367928664c358ef9cdbd))

* fix #37 - improve logging using standard logging module ([`26d7c3e`](https://github.com/RedHatInsights/vmaas/commit/26d7c3e7ca5ce851852b48404c2b69835f65bd32))

* fix #203 - skip found updates not associated with any repo ([`1de8fc7`](https://github.com/RedHatInsights/vmaas/commit/1de8fc749e0f04254c1ceff9f9842d4ffaa18179))

* fix TypeError: Parser must be a string or character stream, not NoneType ([`9758672`](https://github.com/RedHatInsights/vmaas/commit/9758672f29f867d55b72a28a8e06786d0c07595a))

* fix TypeError: Parser must be a string or character stream, not NoneType ([`a512423`](https://github.com/RedHatInsights/vmaas/commit/a5124237a8107e757e044bf0b941d13f2fe722e5))

## v0.3.0 (2018-04-06)

### Unknown

* change to group repo ([`1ff8eb5`](https://github.com/RedHatInsights/vmaas/commit/1ff8eb50f5d4da87580464f0991e472eaaf8eebb))

* updated api doc with modified_since ([`93f3414`](https://github.com/RedHatInsights/vmaas/commit/93f3414ede54f59412d3059cf9d8bc42a6883fee))

* enable modified_since filtering on /errata ([`ac3a386`](https://github.com/RedHatInsights/vmaas/commit/ac3a38664761ec083e8198720dfb0d004a61fe7a))

* fixed wrong response in case of empty errata list ([`4e3a13b`](https://github.com/RedHatInsights/vmaas/commit/4e3a13b54f46ff99e30f9bface76c10e1a07d646))

* install dateutil also in CI ([`8eb46ea`](https://github.com/RedHatInsights/vmaas/commit/8eb46ea44940604445c3e2dadb5b7ee70bf55374))

* add dateutil into containers ([`f2e1bce`](https://github.com/RedHatInsights/vmaas/commit/f2e1bce235511afbc4ebd5a2d3828b538275b4d8))

* use date parser from standard library also in reposcan ([`0cee0ed`](https://github.com/RedHatInsights/vmaas/commit/0cee0edbb59dd5b9973cbf60829ef2baf495751d))

* enable modified_since filtering on /cve ([`b4b5a78`](https://github.com/RedHatInsights/vmaas/commit/b4b5a78fc8d68e5fbab6afef70761ec808362f29))

* add request and response schemas and examples ([`f29ab99`](https://github.com/RedHatInsights/vmaas/commit/f29ab9907e47700a4cc66700845f73ab64b10c82))

* fix #192 - set some CORS headers required by Swagger UI for all requests ([`47699fc`](https://github.com/RedHatInsights/vmaas/commit/47699fc86f58253f5cba9c5396b849e4dc7a6e17))

* set scheme ([`da10ac8`](https://github.com/RedHatInsights/vmaas/commit/da10ac8fe34672e8b57611fe9623d9a10656ce06))

* split handlers into groups ([`52cb900`](https://github.com/RedHatInsights/vmaas/commit/52cb900505a1210560d16583034bea00a629d3e0))

* describe parameters ([`799259d`](https://github.com/RedHatInsights/vmaas/commit/799259dacec70e0de1a89b9ae82b04c89c2c0ba3))

* add % to handler regex to match urlencoded requests ([`6c703e6`](https://github.com/RedHatInsights/vmaas/commit/6c703e6071fd489b8995820653846c459395bb54))

* name parameters in handlers ([`bf67927`](https://github.com/RedHatInsights/vmaas/commit/bf679273aeaf7989fd122673ee1bccf1264253d7))

* make configurable API_URLS ([`71f736b`](https://github.com/RedHatInsights/vmaas/commit/71f736bf4ef8e1f5829f8e82345c0c22c32bf947))

* split single env file to multiple files to not export everything to every container ([`5a67d76`](https://github.com/RedHatInsights/vmaas/commit/5a67d765a8357b16d6a7902e1061a8eff1eeb4e4))

* rebuild swagger ui image with workarounded permissions to make it work in openshift ([`6f5a8c9`](https://github.com/RedHatInsights/vmaas/commit/6f5a8c91981bdf3dccaeb9b9cf0742adef37ad6e))

* cli: additional fix for the commit 749b1e5b.
This fixes TypeError: __init__() takes exactly 3 arguments (2 given) ([`5e5edcf`](https://github.com/RedHatInsights/vmaas/commit/5e5edcf59c89c401b7657b186342df7bdc135a9b))

* api: updates: add RPM arch compatibility checking. ([`d395580`](https://github.com/RedHatInsights/vmaas/commit/d39558003d00c32683c10d780ea434cc91060df5))

* fix #176 - added basearch and releasever details to /updates output ([`7f246a7`](https://github.com/RedHatInsights/vmaas/commit/7f246a7f174b1792955c0a3eae0c2809ac837fa8))

* fix #151 - return also security updates without associated CVEs ([`dd516da`](https://github.com/RedHatInsights/vmaas/commit/dd516da513ead62eb86538a3ef7073455a0f9678))

* Refactor to prevent pylint warnings in errata api ([`8fa0966`](https://github.com/RedHatInsights/vmaas/commit/8fa09662a4d353343f306d586ab364c8886a5239))

* Fixes #185 - relax NOT NULL constraint on fields we have no control over ([`3a4a050`](https://github.com/RedHatInsights/vmaas/commit/3a4a050864c3e65d4dfad4f949f894e0474e99e7))

* fix various pylint issues, intentionally disable arguments-differ on get and post methods because apispec can&#39;t recognize these methods if *args and **kwargs are included ([`bb5aec7`](https://github.com/RedHatInsights/vmaas/commit/bb5aec7f9bcdea129ef4480577233ed0ac0a2911))

* install apispec in travis ([`0830ac8`](https://github.com/RedHatInsights/vmaas/commit/0830ac82a57da9b0d74284eabebc065ae8d076a2))

* enable swagger UI container for both webapp and reposcan APIs ([`aa23f11`](https://github.com/RedHatInsights/vmaas/commit/aa23f11dcc97403b7d4f66298505b096c55e8704))

* split GET and POST handlers because they have different signature ([`30ae199`](https://github.com/RedHatInsights/vmaas/commit/30ae19943364368f7dcbc7be610678333a52b233))

* update webapp docstrings to match apispec requirements ([`059a44e`](https://github.com/RedHatInsights/vmaas/commit/059a44e1d4ea93acaa05873faa9cd92876c5bb62))

* provide apispec API in webapp ([`97e4119`](https://github.com/RedHatInsights/vmaas/commit/97e411934ded3314edcb9d3c72372103d2480cbc))

* update reposcan docstrings to match apispec requirements ([`27e8676`](https://github.com/RedHatInsights/vmaas/commit/27e86760c6e1123775399997171d2a10583aef3f))

* provide apispec API in reposcan ([`2aa174b`](https://github.com/RedHatInsights/vmaas/commit/2aa174b7d710ce323d1567fad76d2383aaa6f178))

* install python-apispec in webapp ([`450fd39`](https://github.com/RedHatInsights/vmaas/commit/450fd39ec75dc4fe9497eca4764a427782b59686))

* install python-apispec in reposcan ([`5ac16f8`](https://github.com/RedHatInsights/vmaas/commit/5ac16f8feca887b255118089040c427e18b2176f))

* specfile for python-apispec package ([`e3f54f7`](https://github.com/RedHatInsights/vmaas/commit/e3f54f70df6e2a51c07e6d3cb8accfe65b09086c))

* do not ignore spec files ([`92d41c1`](https://github.com/RedHatInsights/vmaas/commit/92d41c164277755b9bde0ce47eaae7dc6b5cc15d))

* fix #175 - fix a test and make pylint happy ([`6675472`](https://github.com/RedHatInsights/vmaas/commit/66754723bb02012db2d4fa289c4ace2ce36e19b4))

* fix #175 - add new summary/description for packages ([`9925496`](https://github.com/RedHatInsights/vmaas/commit/99254969a7b3019fda52a90739d53707e5c35028))

* api: updates: add information about compatible package archs into DB. ([`e643236`](https://github.com/RedHatInsights/vmaas/commit/e6432361bfba0d7bf47c2b178bf4ef2b1ddfaa73))

* fix #145 - Disallow empty strings in db

* Checkconstraint for empty on all TEXT fields
* Teach cve_store to store null instead of &#39;&#39; when no-url-found
* Teach updateinfo to store null if field is empty/white-space-only
* Teach repository_store to store null instead of empty-string for key ([`7f0d744`](https://github.com/RedHatInsights/vmaas/commit/7f0d744681c34a008d10db3d45c641275c976b68))

* fixed format of /cve response ([`c8ea3cb`](https://github.com/RedHatInsights/vmaas/commit/c8ea3cb09849514dd65c59dda868c1a494a95d9e))

* fix #166 - encapsulate responses and take advantage of tornado to set Content-Type to app/json ([`dfd83f4`](https://github.com/RedHatInsights/vmaas/commit/dfd83f475d5ad84ebdb2cd4617131b2f6a471de7))

* search updates in all repositories provided by same product but with same releasever ([`237af1d`](https://github.com/RedHatInsights/vmaas/commit/237af1d71ebaebb8f404bd07e189d687db58b6b3))

* define mappings for repo and product ids ([`422c585`](https://github.com/RedHatInsights/vmaas/commit/422c5858438c6f24588b8ad546119f18bfd78d0d))

* iterate directly over values

so we don&#39;t need lookup them over and over ([`0785611`](https://github.com/RedHatInsights/vmaas/commit/078561118ba087455cf20323364a8a4a73ec5083))

* simplify code with setdefault() ([`ed8575b`](https://github.com/RedHatInsights/vmaas/commit/ed8575b1fa9ab137d9ca58e89935b583a5bd6b39))

* comments to algorithm steps ([`e92d93d`](https://github.com/RedHatInsights/vmaas/commit/e92d93dfcb3042693ed9b5ce080d88f0865954b4))

* don&#39;t parse package name over again, remember it ([`8ac4b27`](https://github.com/RedHatInsights/vmaas/commit/8ac4b27d6d23d42bd2614476c5a2924fa23151d6))

* updated  docstring ([`0868e35`](https://github.com/RedHatInsights/vmaas/commit/0868e3549942dda7b51076bcf400f576edabc171))

* fixed wrong response in case of empty package list ([`de15a0e`](https://github.com/RedHatInsights/vmaas/commit/de15a0ee82f29ad467d48c9c1a8d4cdfe9edb16c))

* added updates filtering by repo releasever and basearch ([`28ac550`](https://github.com/RedHatInsights/vmaas/commit/28ac5505a137e2d5cbeed8a712cb883d10d66e27))

* fix #116 - output timestamps in ISO 8601 format ([`7cac052`](https://github.com/RedHatInsights/vmaas/commit/7cac05253285aeb44a965eee73c49b536b9b007e))

* fix #116 - parse errata datetimes on application level and include tzinfo ([`4a622e3`](https://github.com/RedHatInsights/vmaas/commit/4a622e3275921871d91dfe03cf1392fbaa3587a7))

* fix #116 - add tzinfo to timestamps to properly import to PostgreSQL ([`28c16ab`](https://github.com/RedHatInsights/vmaas/commit/28c16ab81a334f770e9e0505f8780b63bbfc8f11))

* fix #116 - convert to datetime object immediately and import to PostgreSQL without to_timestamp() conversion

custom utc implementation is needed in Python &lt; 3 ([`bbd7f96`](https://github.com/RedHatInsights/vmaas/commit/bbd7f964b43b8abbfaf2aa2eb291fb3fb9820441))

* include revision of repository in API output ([`3ffdafd`](https://github.com/RedHatInsights/vmaas/commit/3ffdafd75c73b37b85b4179bf974a0966bf8a8d5))

* fix #116 - change all timestamp columns to contain timezone ([`d71aadd`](https://github.com/RedHatInsights/vmaas/commit/d71aaddfd8a403e66b611afb2db82965dbdf15dd))

* test fixes - added latest errata and repo details ([`f5ca429`](https://github.com/RedHatInsights/vmaas/commit/f5ca429dabd812a45831bb1f2788bd1b83ad8edd))

* test fixes - reformat api output to match sorted json ([`73d4ff2`](https://github.com/RedHatInsights/vmaas/commit/73d4ff2472a229cb1dd9035a6563db4770055bd4))

* test fixes - sort json output to make it diff-able ([`48a12c8`](https://github.com/RedHatInsights/vmaas/commit/48a12c8871157197941b4919f67b0043534e0252))

* fix #168 - refresh repocache after reposcan ([`00b7725`](https://github.com/RedHatInsights/vmaas/commit/00b772528f37c6176fcb8838cb720c7344c3e6da))

* fix #158 - re-applying changes from &#34;#142 - resuse RepoCache in UpdateAPI&#34;

cherry pick from 749b1e5b5c79d9388d73f87a34fb73feb29afbd0 ([`b6126b9`](https://github.com/RedHatInsights/vmaas/commit/b6126b9076a06ec79605fa50e5d158adcf1e973e))

* fix #158 - fixing merge of &#34;#142 - resuse RepoCache in UpdateAPI&#34;

partially reverts commit 749b1e5b5c79d9388d73f87a34fb73feb29afbd0. ([`acc1ebf`](https://github.com/RedHatInsights/vmaas/commit/acc1ebfd8e714c62e63bedbcb7c84067f11a31b9))

* simple test for API output

mainly for manual sanity tests
not suitable for travis because it requires working application incl. loaded data ([`7950a44`](https://github.com/RedHatInsights/vmaas/commit/7950a44d0d97824ea61bc9abf23f6a965f18f92b))

* #142 - update example in README ([`14c4006`](https://github.com/RedHatInsights/vmaas/commit/14c400628430ac7ed41bd609e85792e566864205))

* #142 - update repository test to use new header ([`fcd0681`](https://github.com/RedHatInsights/vmaas/commit/fcd0681ac1c9e355f4100387d4f13d00ad699b99))

* #142 - remove repo label, make content set label mandatory and fill missing values ([`c49165c`](https://github.com/RedHatInsights/vmaas/commit/c49165c37daf24f70a8804f25bbee414d65a78ce))

* #142 - expand content sets urls to repo urls ([`4384bf6`](https://github.com/RedHatInsights/vmaas/commit/4384bf6d1c7a58492969f1d10fa79c2656957c10))

* #142 - repo name is the main attribute for products, not the optional product id ([`c387829`](https://github.com/RedHatInsights/vmaas/commit/c387829ef2e8e55ef62ba90cd1293b2bcf7ddd60))

* #142 - simple repo list format is not supported anymore ([`ac6fd2b`](https://github.com/RedHatInsights/vmaas/commit/ac6fd2bf23eae79cfb091b4e241ac24d266f1068))

* #142 - include example input repolist for the sync API ([`40364cb`](https://github.com/RedHatInsights/vmaas/commit/40364cbf7fbabb975b5368ab0d81b73ffc353a68))

* #142 - product name is now unique and product id is now optional ([`d772dff`](https://github.com/RedHatInsights/vmaas/commit/d772dff76b048f1e61e98cbeb3cdb156e84f1fcb))

*  #142 - resuse RepoCache in UpdateAPI ([`749b1e5`](https://github.com/RedHatInsights/vmaas/commit/749b1e5b5c79d9388d73f87a34fb73feb29afbd0))

*  #142 - repo labels on client are actually content set labels

fetch and store the whole key table at the app init ([`fddf86d`](https://github.com/RedHatInsights/vmaas/commit/fddf86d810e5f622da083fe64d237b500578dbc1))

* api: updates: pylint: fix too-many-nested-blocks. ([`26a69d2`](https://github.com/RedHatInsights/vmaas/commit/26a69d21e03abb6cb7edb92723fca8fd6156edb6))

* api: updates: pylint: fix invalid names. ([`3fbf4b3`](https://github.com/RedHatInsights/vmaas/commit/3fbf4b3e5dc98f8478ceff9b2d74ff3ec83309fa))

* Update cve api with cvss3_score ([`b6f364b`](https://github.com/RedHatInsights/vmaas/commit/b6f364bc36d486487cc40f187dbe0c8c2435f9fd))

* rework errata api implementation to fill errata lists with 3 db queries instead of 3 queries for each erratum ([`9980fe7`](https://github.com/RedHatInsights/vmaas/commit/9980fe7c5f07feecdf78f0fc7dd56334acd825ab))

* add bugzilla and other references lists to errata ([`25a2587`](https://github.com/RedHatInsights/vmaas/commit/25a2587addf1c8b306fce7c81bbb0a7f500ba95b))

* simple periodic sync of repos and CVEs ([`82ac1ae`](https://github.com/RedHatInsights/vmaas/commit/82ac1aead36f1a9de6de6d34e92f5e9a2ac5aa16))

* rollback any pending transaction when error occurs in repo or cve scan ([`7ddb769`](https://github.com/RedHatInsights/vmaas/commit/7ddb7696a55012103ec1366de4d5fa8175e4fab8))

* hint PostgreSQL to cast NULL values properly ([`6e4d312`](https://github.com/RedHatInsights/vmaas/commit/6e4d3121f188538f4194b9ce9e87534a0407d1fc))

* specify internal port number in docker-compose config to propagate into openshift deployment config ([`7ad1484`](https://github.com/RedHatInsights/vmaas/commit/7ad14842c0a3fc317f67496e9b08a4f82029d994))

* fix errata api bug introduced in pr143 ([`d7facf6`](https://github.com/RedHatInsights/vmaas/commit/d7facf6013e0cd473e747d3b7cf8317c2ddb94a8))

* allow to call the refresh API on internal port only ([`ef91587`](https://github.com/RedHatInsights/vmaas/commit/ef91587efca17ea5cd4222f5a66bc177df4346a7))

* provide webapp API to refresh it&#39;s cached data and call it after reposcan run ([`b4cc476`](https://github.com/RedHatInsights/vmaas/commit/b4cc476614f541bca66c8949a4b649df01d7fd50))

* print traceback to the stdout

simplifies debugging when you can see what happend ([`1512753`](https://github.com/RedHatInsights/vmaas/commit/15127531192bb442c40d329d6520a2b39dea5200))

* simplify key building

and make it slightly faster ([`7a8bbe3`](https://github.com/RedHatInsights/vmaas/commit/7a8bbe317aa9f576086c72d132f48b4ad9ccd202))

* move package name splitting into shared module ([`1f70229`](https://github.com/RedHatInsights/vmaas/commit/1f702294469dd86164b8a71d8229887e94aecf2e))

* make a shared function for building package name from nevra

and deduplicate code ([`7122535`](https://github.com/RedHatInsights/vmaas/commit/712253564d3a488e33239b9ef1b458b5fc8f491a))

* simplify setattr/getattr code ([`5558fc7`](https://github.com/RedHatInsights/vmaas/commit/5558fc7627f211daebe69f53d2c4b1a2416fe715))

* add name, arch and releasever columns ([`db1ab24`](https://github.com/RedHatInsights/vmaas/commit/db1ab24d99d370c71aa51dfd5545de5c0587416b))

* refactoring: rename repo name -&gt; repo label ([`0c9a4a3`](https://github.com/RedHatInsights/vmaas/commit/0c9a4a3ef079519ae4151ad0c382b23e6223c449))

* fix input package with invalid architecture ([`1e56c12`](https://github.com/RedHatInsights/vmaas/commit/1e56c1211a296c14fe32cf4a29919ca2835fe560))

* add missing type and summary fields to errata ([`4d69c36`](https://github.com/RedHatInsights/vmaas/commit/4d69c367d80f28711073167c4a76fc444f850919))

* api: updates: fix issue #115. API method updates should return security-related erratum by default. ([`c2c88f8`](https://github.com/RedHatInsights/vmaas/commit/c2c88f8a8beffa0e2f28791bfd12da690159ac6b))

## v0.2.0 (2018-03-15)

### Unknown

* import CVE by year in ascending order ([`70976bc`](https://github.com/RedHatInsights/vmaas/commit/70976bcf8847d97bd4962ccd9b8ca265fae16a85))

* sync even older CVEs ([`94faa7e`](https://github.com/RedHatInsights/vmaas/commit/94faa7e0d80c409ea0eb8f0412818e874b622373))

* Fix inserting null-values into cwe_cve table ([`b6fadca`](https://github.com/RedHatInsights/vmaas/commit/b6fadca60c1870377c34eaec59697993ddf686ff))

* pylint: fixed long line ([`c33b45b`](https://github.com/RedHatInsights/vmaas/commit/c33b45b2cebd04590af7b5bead54d034fe3c643c))

* pylint: disable abstract-method warning for handler classes ([`4202cbd`](https://github.com/RedHatInsights/vmaas/commit/4202cbd1a0578bbd04d94bc448a488fb4f85a3e0))

* pylint: fixed parameters differ from overridden method ([`20794ea`](https://github.com/RedHatInsights/vmaas/commit/20794eaa63e2f3fa378a48421d7efabfc58a40dc))

* pylint: temporarily disabling warnings to enable other pylint checks
        sooner than later ([`756129b`](https://github.com/RedHatInsights/vmaas/commit/756129b9adc12e36e40006e1cb94248396ba298d))

* move lookup dictionary building from each request into application startup

peformance improvement
partially fixing too-many-statements/too-many-locals/too-many-branches ([`2f0035f`](https://github.com/RedHatInsights/vmaas/commit/2f0035f14fbc16085ebc942cdb3d9806c57db500))

* pylint: fixed invalid variable name &#34;e&#34; ([`c427a15`](https://github.com/RedHatInsights/vmaas/commit/c427a15340402eba3d14b750dc4aebdadeb73206))

* pylint: fixed old-style class defined ([`53b5e8b`](https://github.com/RedHatInsights/vmaas/commit/53b5e8b40e5bdb59fcc3123c41046db28aca3723))

* pylint: disable too-few-public-methods warning ([`5a22574`](https://github.com/RedHatInsights/vmaas/commit/5a22574b51c531bcb2335f81103b02fb02692e43))

* pylint: fixed using variable &#39;response&#39; before assignment ([`ea5213e`](https://github.com/RedHatInsights/vmaas/commit/ea5213e12d6cc86367b8e088308eef6824054a0d))

* pylint: disabled warning for n, e, v, r, a variable names ([`70a0f89`](https://github.com/RedHatInsights/vmaas/commit/70a0f898eab2796411488b554d4a94a9d8ee10ec))

* pylint: fixed redefining built-in &#39;id&#39; ([`13cbf6d`](https://github.com/RedHatInsights/vmaas/commit/13cbf6d9e0f31dcd75b09d8400fe75865d215705))

* pylint: fixed consider-iterating-dictionary ([`5afca73`](https://github.com/RedHatInsights/vmaas/commit/5afca73ce3c6cee166709cca4577dbd09b165e83))

* pylint: fixed indentation and whitespace ([`3c2b562`](https://github.com/RedHatInsights/vmaas/commit/3c2b562ff9484cb6b5cab129e744a69fdd26feba))

* pylint: disable too-many-arguments/too-few-public-method for Database class ([`eec7afe`](https://github.com/RedHatInsights/vmaas/commit/eec7afe34148c6fb83845c154caf49c0df34f0fb))

* pylint: parent class should contain abstract methods ([`282d998`](https://github.com/RedHatInsights/vmaas/commit/282d9983623f3f121c2720fba3403a7994064329))

* pylint: fixed imports and shebang ([`8569b79`](https://github.com/RedHatInsights/vmaas/commit/8569b7900d2b3bfb444b9f5aca0526f6a16b4d0f))

* pylint: fixed missing class docstrings ([`e6aaa7b`](https://github.com/RedHatInsights/vmaas/commit/e6aaa7bebaa5320f7b4fbeb992b94fcabf9a6d98))

* run python tests also in webapp ([`0b9a513`](https://github.com/RedHatInsights/vmaas/commit/0b9a5133dd1cfb06e32c10cec18780307d6705ab))

* Edit CVE select to use column_names ([`0bbce12`](https://github.com/RedHatInsights/vmaas/commit/0bbce12058d238faf7707efd5a9ca12b52938d23))

* Make datetime human readable in CVE api ([`20f0ab9`](https://github.com/RedHatInsights/vmaas/commit/20f0ab98b0e15d345d852f9bec032cde0b857b8d))

* Remove iava from cve api response ([`c5cdfbb`](https://github.com/RedHatInsights/vmaas/commit/c5cdfbbc24e78eb85df9bf0d7b56803cd5f9ca12))

* api: updates: Issue #124. In many cases, we can have an empty data during SQL request.

This commit adds checking of data before making a SQL request to the DB.
In case if there is no package from the input list which matches packages in the DB, return an empty result
immediately. ([`5ea4942`](https://github.com/RedHatInsights/vmaas/commit/5ea4942993c8fa1317f2d0aa17b0447a5be38df9))

* make long sql more readable and use variable binding

prevents sql injection ([`49603ff`](https://github.com/RedHatInsights/vmaas/commit/49603ff9d29a9d411a681b3cc8096a6585ec1272))

* api: remove outdated doc handler.
This doc handler was used for debug purpose only and now outdated.
We are not going to support documentation in this place. ([`d07c6ed`](https://github.com/RedHatInsights/vmaas/commit/d07c6ed23cfaad9ed674ec4e219e5a819b3255cd))

* api: cli: additional fixes for 06d1ffad577535dbb0c432ccb13bee8259077696.
all API methods are implementeed as classes, so we need to instantiate them and use their methods. ([`720bae6`](https://github.com/RedHatInsights/vmaas/commit/720bae6d6f0b7666f9f100489431e2611736b3dc))

* remove remaining occurences of ujson ([`48cf564`](https://github.com/RedHatInsights/vmaas/commit/48cf564307d5e4d711d3f7238f269dec8b0a3018))

* api: use python json module from the standard library, instead of ujson from epel.
Since we are not using ujson anymore, &#39;epel&#39; repository is also removed.

Removed some unused imports:
&#39;import os&#39; in webapp/app.py
&#39;import sys&#39; in webapp/repos.py ([`b2fcc5f`](https://github.com/RedHatInsights/vmaas/commit/b2fcc5f5f65fea5194d6ad274436815226e09ac8))

* api: according to the official documentation to write the output to the network we need to use the flush() method.
http://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write ([`0e37c5e`](https://github.com/RedHatInsights/vmaas/commit/0e37c5e414f0ec0837ba7bd888a0e116ab9a04f2))

* api: use JSON auto-formating by Tornado.
It also sets Content-Type: application/json; charset=UTF-8 ([`845a805`](https://github.com/RedHatInsights/vmaas/commit/845a805498c56cd0adea152f9e3b36c2ccd5c253))

* Issue 67 - set connection to readonly and autocommit ([`8de8ded`](https://github.com/RedHatInsights/vmaas/commit/8de8ded730c97d1fe75e071fa6b8c679f0fcc8b1))

* change example to more useful format for RHSM repos ([`15c9a91`](https://github.com/RedHatInsights/vmaas/commit/15c9a91dd7c5d8b5a56e47474f57057c7cba0ac8))

* api: url for GET requests should be without &#39;/&#39; at the end. ([`7b95b51`](https://github.com/RedHatInsights/vmaas/commit/7b95b517c4bf8ca98f7c068a23b44f1a5523df88))

* Add errata api implementation ([`702c13c`](https://github.com/RedHatInsights/vmaas/commit/702c13c43f2b50538c6b4a5e372893121201e15a))

* moved updates API methods into a class ([`06d1ffa`](https://github.com/RedHatInsights/vmaas/commit/06d1ffad577535dbb0c432ccb13bee8259077696))

* moved cve API methods into a class ([`6a86ee8`](https://github.com/RedHatInsights/vmaas/commit/6a86ee8047c68d9769fced9221df86b53a01aae7))

* api: updates: for GET request handling we need to match packages name.
additional changes for the commit 3eb717cc1b7cc3c01c8af58a86d5e6b93d4cfea7 ([`aad7531`](https://github.com/RedHatInsights/vmaas/commit/aad75315ecd27304655acfd55e326aa702049329))

* support underscores in repo label ([`3241a2c`](https://github.com/RedHatInsights/vmaas/commit/3241a2ce9fdc01f421753123de7942bd99d04414))

* api: updates: fix KeyError: &#39;repo_list&#39;, after renaming it to &#39;repository_list&#39;. ([`8a48b44`](https://github.com/RedHatInsights/vmaas/commit/8a48b446222f2d58c0a61df5f84ccb81c596f211))

* api: updates: add filtering by reponame list. ([`f8262a1`](https://github.com/RedHatInsights/vmaas/commit/f8262a1de5bd14ec322ed5af518239ab21bc5aab))

* de-duplicated code in main() ([`cf1e12e`](https://github.com/RedHatInsights/vmaas/commit/cf1e12ee76cfbeefac34bacfedf9633f2e8b22f6))

* moved duplicated code into procedure ([`4875439`](https://github.com/RedHatInsights/vmaas/commit/4875439fd01a57037e4eb80e061a14231eac109b))

* added repo API to vmaas cli ([`191e793`](https://github.com/RedHatInsights/vmaas/commit/191e7938b1a02b46f47b240b2243592605557e1f))

* api for repository details ([`3d00dbb`](https://github.com/RedHatInsights/vmaas/commit/3d00dbbda951dea91ecb405a7d9a3627a49243c0))

* added missing cli script to image ([`dff6129`](https://github.com/RedHatInsights/vmaas/commit/dff612970850e01b5bf686573062e3ea9d5f3a48))

* reposcan: add information about &#39;reposcan&#39; APIs into README. ([`64538c4`](https://github.com/RedHatInsights/vmaas/commit/64538c449a308a991b6a3752113df7b718efad92))

* fixed cli according to &#34;reusable API changes&#34;

fixes changes in dc49277f8d64ba531256495dc24f3acab646fb65 ([`6d4e89c`](https://github.com/RedHatInsights/vmaas/commit/6d4e89c10cdaa4af3fca4c004038c2a134e96c8e))

* import JSON list with defined products and content sets ([`d1a7e24`](https://github.com/RedHatInsights/vmaas/commit/d1a7e2400afe1004264bf3cee7f99506daac95d6))

* add content_set table and reference it from repo table instead of product directly ([`07169d8`](https://github.com/RedHatInsights/vmaas/commit/07169d8501ceef8e83247b398c18424e5dbbbd73))

* rename eng_product_id to redhat_eng_product_id and make name optional ([`e36a444`](https://github.com/RedHatInsights/vmaas/commit/e36a444976fbfa8d3a4997e29236cc0a8f54caa0))

* Add API to report CVE details ([`9f8ce62`](https://github.com/RedHatInsights/vmaas/commit/9f8ce62e2711b3927e2b3733974234bea3997ea1))

* Fix error response when malformed json input so its not masked by the local variable &#39;response&#39; referenced before assignment error ([`2c57357`](https://github.com/RedHatInsights/vmaas/commit/2c573570d4937d1fc89d28ff89e8cbb98fa686b4))

* Remove unused imports ([`c752264`](https://github.com/RedHatInsights/vmaas/commit/c752264eceaa7c55be82f0a0f61bf06520b3d3a9))

* Fix error in JsonHandler ([`69d3bb0`](https://github.com/RedHatInsights/vmaas/commit/69d3bb0fe3595f7332bf643bd22056239c85c778))

* database.py is missing in image ([`70430ca`](https://github.com/RedHatInsights/vmaas/commit/70430caf3b0195d2d80b2262de752343ed69a168))

* make json file/body handling reusable by other APIs ([`dc49277`](https://github.com/RedHatInsights/vmaas/commit/dc49277f8d64ba531256495dc24f3acab646fb65))

* add script for simple fetching and rebasing pull request

from spacewalkproject/spacewalk ([`b40dbd3`](https://github.com/RedHatInsights/vmaas/commit/b40dbd3890cfb5bf155e7aaf65e35a040351b7ba))

* moved cli stuff into &#39;vmaas&#39; commandline

i.e. `vmaas updates rubygem-psych-2.0.0-33.el7_4.x86_64` ([`9ceeb81`](https://github.com/RedHatInsights/vmaas/commit/9ceeb812942135e83ce19311539201e37e99e329))

* moved database connection code to a module ([`e8cac0c`](https://github.com/RedHatInsights/vmaas/commit/e8cac0c838b018b7578ee09f520bc0e106858e91))

* api: updates: add GET request processing. ([`3eb717c`](https://github.com/RedHatInsights/vmaas/commit/3eb717cc1b7cc3c01c8af58a86d5e6b93d4cfea7))

## v0.1.0 (2018-03-08)

### Unknown

* api: updates: skip only updates w/o erratum associated. ([`02a60fe`](https://github.com/RedHatInsights/vmaas/commit/02a60feef42e71cdd930ba89d923711d9639c461))

* compare last commit only

fixing &#34;fatal: ambiguous argument &#39;HEAD..master&#39;: unknown revision or path not in the working tree.&#34; ([`c66aec7`](https://github.com/RedHatInsights/vmaas/commit/c66aec7fa42cafc65e48a4720820dac07daad5a9))

* TRAVIS_COMMIT_RANGE can be empty ([`959542b`](https://github.com/RedHatInsights/vmaas/commit/959542b3d4c6285f1f9bf5de08e11937fa0ae00a))

* add ansible task to trigger update of docker images from docker hub in a current OS project ([`bc7fde4`](https://github.com/RedHatInsights/vmaas/commit/bc7fde456bd5bd9f2c9e939d2375180d905cb3c0))

* reserve 4 gigabytes for reposcan tmp in OS by default ([`00c06cf`](https://github.com/RedHatInsights/vmaas/commit/00c06cfa0d5383a06b4b0dc17f4b3debf383c2a0))

* rebuild all images when docker-compose config changes ([`51276dd`](https://github.com/RedHatInsights/vmaas/commit/51276dd3027581080470eccfd6386aa87df07057))

* add release script ([`193d42b`](https://github.com/RedHatInsights/vmaas/commit/193d42b25cb84b20eb9406fcc46036033e98297b))

* specify default tag ([`fec4ca0`](https://github.com/RedHatInsights/vmaas/commit/fec4ca0e50faa70418d6acddb592c2bddcf8b46c))

* Fix fatal KeyError when NEVRA not associated with an erratum ([`4d9d961`](https://github.com/RedHatInsights/vmaas/commit/4d9d96102d6731dde4063e5991b77da2cf10d005))

* Add support for parsing CVE links and CWEs ([`ae93eac`](https://github.com/RedHatInsights/vmaas/commit/ae93eace7db13bdd40b040d022c39e06ba9ccf0c))

* added developer setup instructions ([`e775dbd`](https://github.com/RedHatInsights/vmaas/commit/e775dbd6c9f0df185abbc0851565c7478727d7c4))

* script to simplify developer setup management ([`088f83b`](https://github.com/RedHatInsights/vmaas/commit/088f83b23e0e52551d3d79c33a9f5a866143d514))

* create standard way run apps in different containers

to simplify development - every subservice uses ./entrypoint.sh to start ([`a6480e2`](https://github.com/RedHatInsights/vmaas/commit/a6480e250a2c8f7d0e3358d908517a94e74d8c25))

* create developer setup

basic definition are in docker-compose.yml and docker-compose.devel.yml
just modifies them for easier testing/debugging directly from git

webapp and reposcan also don&#39;t run default container command but
let developers to run/debug processes manually instead ([`cfa357a`](https://github.com/RedHatInsights/vmaas/commit/cfa357a07dba0bf8678addc3ab6abc2a2617930b))

* Added a &#39;what is this thing?&#39; section to README ([`e93130b`](https://github.com/RedHatInsights/vmaas/commit/e93130b8fc1ca4684ed215c7c8ecbefa1a23d884))

* api: updates: take into account architecture of a package.

Use exact matching for architectures. ([`a2bc12d`](https://github.com/RedHatInsights/vmaas/commit/a2bc12d08ade880febf3853a9678aa7baff180a0))

* Update README.md ([`fe77ceb`](https://github.com/RedHatInsights/vmaas/commit/fe77cebb1e5df81dd7760b2427bb1b5fa6de5d22))

* api: updates: fix issue #70 - output has missing results.

Errata can be associated with several repos, so now we are checking package repo IDs matching to some errata repo IDs. ([`ed8048b`](https://github.com/RedHatInsights/vmaas/commit/ed8048ba9b81804c535c847dab24873e5ff65159))

* api: updates: use PEP8 naming convention. ([`acffbb7`](https://github.com/RedHatInsights/vmaas/commit/acffbb702290b5763e57c20b21dc092b0ad6c874))

* api: updates: remove issue list from the source code.Lets track all of them on github.
We, defenetely, do not check/update this list here. ([`d61175e`](https://github.com/RedHatInsights/vmaas/commit/d61175e8df30b33bb2a9a53aa334e16b8fdb30d8))

* api: updates: remove obsolete and unused methods. ([`3ce8886`](https://github.com/RedHatInsights/vmaas/commit/3ce8886937b998866daf0a7f42d2397b102acead))

* api: updates: add python docstring for &#39;process_list&#39; method. ([`2a909d8`](https://github.com/RedHatInsights/vmaas/commit/2a909d8064ff2a60d8018ac60999293b4d0e4c0f))

* EPEL is needed because of python-ujson ([`a1dba6c`](https://github.com/RedHatInsights/vmaas/commit/a1dba6c6cad518a48c8d77c685980265d942bb73))

* api: fix Dockerfile after renaming errata.py to updates.py. ([`24e3173`](https://github.com/RedHatInsights/vmaas/commit/24e3173584e12f82af297ea152e55eb239274f26))

* don&#39;t continue after error ([`5c58612`](https://github.com/RedHatInsights/vmaas/commit/5c58612437d9b86b4e0142a8ef6f3086e1284602))

* api: rename errata module to more appropriate updates. ([`59434ed`](https://github.com/RedHatInsights/vmaas/commit/59434ed28c6df6367f10059533e4238aa47cf24a))

* save downloaded files outside the application container ([`fe83268`](https://github.com/RedHatInsights/vmaas/commit/fe83268fb5bf9c7635bfd652cb51b501be2e43ae))

* remove unused python2-falcon dependency

sys isn&#39;t used too ([`b684e05`](https://github.com/RedHatInsights/vmaas/commit/b684e0546172a05032c55e228ee02be8ae6ee7eb))

* add build status icon ([`8bf11fa`](https://github.com/RedHatInsights/vmaas/commit/8bf11faf903f26314ec990b80fd1c74c7f921930))

* api: fix issue #64, fix format of output json for &#39;updates&#39; API. ([`6cc32bd`](https://github.com/RedHatInsights/vmaas/commit/6cc32bdfffd645ec306f6c229b0ceb51305ec08c))

* merge &#39;utils&#39; and &#39;scripts&#39; directories. ([`b9ac792`](https://github.com/RedHatInsights/vmaas/commit/b9ac7923d0cfc3cbebce0ff9a869b544f7539d4a))

* api: rename JsonHandler to UpdatesHandler, remove unnecessary information from the response. ([`b309adb`](https://github.com/RedHatInsights/vmaas/commit/b309adbb9fb0cb6894e49fd55eabe3feca1c0bd3))

* api: remove obsolete PlaintextHandler ([`aec377d`](https://github.com/RedHatInsights/vmaas/commit/aec377d0dd8a4dbe1567ee72ea2fa8cf0704954a))

* api: rename MainHandler to more apropriate DocHandler ([`328870e`](https://github.com/RedHatInsights/vmaas/commit/328870e8cdefa5a382bbf2a3a0f32b4d5eef7a4f))

* use repository names properly ([`9ac26ef`](https://github.com/RedHatInsights/vmaas/commit/9ac26ef8fc09ca2e10368965da17fbfda089937f))

* transform reposcan to API service and join with cvescan ([`25b1e1c`](https://github.com/RedHatInsights/vmaas/commit/25b1e1c9e3a22043e5fd75685409cc81c08ca339))

* add ujson module to fix pylint

E: 92,15: Module &#39;ujson&#39; has no &#39;dumps&#39; member (no-member) ([`11a8909`](https://github.com/RedHatInsights/vmaas/commit/11a8909841e11b658968c953cbb840239c5e9b99))

* store certificate in DB and support syncing all previously synced repos ([`ed6b9aa`](https://github.com/RedHatInsights/vmaas/commit/ed6b9aab5c0d0794d3d56b7d6d9270ded554288c))

* support to download from https repositories ([`8ac6661`](https://github.com/RedHatInsights/vmaas/commit/8ac66611f4ab00d858141ef350c13fed9f4c8408))

* increase number of valid instance attributes ([`cb4f283`](https://github.com/RedHatInsights/vmaas/commit/cb4f283f8fc2350b530d6a09ee2fb1e94beb36ee))

* add utils directory and &#39;rpm-json&#39; to convert rpm list to vmaas input json format ([`5315961`](https://github.com/RedHatInsights/vmaas/commit/531596138a61be585d2d953ca4405be0ae68a8be))

* update the docstring to match the new behavior ([`f8eafce`](https://github.com/RedHatInsights/vmaas/commit/f8eafce1d8f46f3021c960f3c40aaa6394ec3364))

* api: issue 57, change way of parsing RPM package name ([`d7dff65`](https://github.com/RedHatInsights/vmaas/commit/d7dff65b7b6a3bf484a23021c95755c6b55b83a1))

* unit tests for nistcve importer ([`3fce7db`](https://github.com/RedHatInsights/vmaas/commit/3fce7db4f56103677c17fd39af6ba3497ef010fb))

* added missing docstrings ([`ab0cd72`](https://github.com/RedHatInsights/vmaas/commit/ab0cd7254de28b12e4c1f93c522e4b7204f2b78a))

* disable similarity check

will fix them and re-enable it later ([`c860c68`](https://github.com/RedHatInsights/vmaas/commit/c860c684237c01ca9623580944ae2950d9c05ec2))

* initial version of NIST CVE downloader ([`da61123`](https://github.com/RedHatInsights/vmaas/commit/da611237e2aad0bc51994ee1d83056473c94d236))

* extended cve table with additional attributes ([`4ea328d`](https://github.com/RedHatInsights/vmaas/commit/4ea328d0d2da8e149572531af40d657d89c4b6c2))

* metadata table

to hold persistent state of vmaas processes,
e.g. import file timestamps ([`7176f9b`](https://github.com/RedHatInsights/vmaas/commit/7176f9bcebd27798b681788a50ce181faaae3c98))

* api: add method to process input packages list and make result in format:

&#39;package_name&#39;: [
    [&#39;package_to_update1&#39;, &#39;errata_name1&#39;, &#39;repo_name1&#39;],

    ...

    [&#39;package_to_updateN&#39;, &#39;errata_nameN&#39;, &#39;repo_nameN&#39;]
] ([`6be821a`](https://github.com/RedHatInsights/vmaas/commit/6be821afad80d81ed1b2ea8c70c279f506fd3a58))

* build and push docker images after succesful push into master ([`abe6265`](https://github.com/RedHatInsights/vmaas/commit/abe62653e2415434defa6128ccb639dc07d1dbd3))

* add OpenShift deployment playbook ([`b9ea5d8`](https://github.com/RedHatInsights/vmaas/commit/b9ea5d8b36402e7bd10816bbf6fe0aa87e654b0a))

* upgrade to Docker compose V3 for better Kompose support and rename variables to work in OpenShift ([`d973cf0`](https://github.com/RedHatInsights/vmaas/commit/d973cf0191d19725330b17a353debbc9e49d3a5b))

* define volume for PostgreSQL database ([`72033c8`](https://github.com/RedHatInsights/vmaas/commit/72033c83f3cfb654ef72a45e8259aa4a66d40596))

* switch from original postgres image to centos/postgresql-96-centos7 because it can&#39;t be deployed in OpenShift

this image is using slightly different name for variables -&gt; rename ([`a3ff9a7`](https://github.com/RedHatInsights/vmaas/commit/a3ff9a7600de507995af3f4da0c778c5f1f2d626))

* change image names to match vmaas Docker Hub org ([`26f9357`](https://github.com/RedHatInsights/vmaas/commit/26f93571782b9425d9eb694a46f713f49942cc54))

* _really_ fix style issues ([`1875e7a`](https://github.com/RedHatInsights/vmaas/commit/1875e7a26d59355e2678ff33a8df825fffdad51c))

* Fixing style issues ([`27773c8`](https://github.com/RedHatInsights/vmaas/commit/27773c8d731ab9e28f804d4d5be0be31251c30ae))

* Fill in more errata metadata ([`bee1da2`](https://github.com/RedHatInsights/vmaas/commit/bee1da21574463282d1d48108765d5d04656cd6a))

* Change setup instructions to use docker from fedora repos ([`c981add`](https://github.com/RedHatInsights/vmaas/commit/c981adde843ac0f22efb362b4133feac93b1e529))

* Update README.md with initial setup instructions ([`b2f9105`](https://github.com/RedHatInsights/vmaas/commit/b2f91053133f7fecf6d58718e77f82f63a05af1e))

* fixing too-many-branches, too-many-locals, too-many-statements ([`da5c857`](https://github.com/RedHatInsights/vmaas/commit/da5c8579e01ec6e5ec8df7ac728b8a02d4029278))

* fixing duplicate-code ([`609e301`](https://github.com/RedHatInsights/vmaas/commit/609e301378ef7d3a79d3def8b502367d5a143c3b))

* fixing invalid-name ([`cb52707`](https://github.com/RedHatInsights/vmaas/commit/cb527076ea751a1e961780f0b69fca6434498d36))

* do not complain about these words in comments ([`e9aa235`](https://github.com/RedHatInsights/vmaas/commit/e9aa2358cd679f1dbf371a7e8344e1c3fd164ceb))

* fixing bad-continuation ([`3c8ea5d`](https://github.com/RedHatInsights/vmaas/commit/3c8ea5d2a48981de68ae4bc03b3e481db3f9cb7f))

* fixing no-else-return ([`cac88d3`](https://github.com/RedHatInsights/vmaas/commit/cac88d355c994de8494f37be382a5ed818c3bc1a))

* remove unused variable ([`5357b3a`](https://github.com/RedHatInsights/vmaas/commit/5357b3a7858d7726c97a90e0c3b5e7344f76d5f0))

* disabling too-few-public-methods for some classes ([`4af20de`](https://github.com/RedHatInsights/vmaas/commit/4af20dec3884ab6ff9685a3daec725f8f05e3981))

* fixing line-too-long ([`296c849`](https://github.com/RedHatInsights/vmaas/commit/296c8497a66f0f9ac8559523c4b58b9d61c9237b))

* fixing len-as-condition ([`8c81d0f`](https://github.com/RedHatInsights/vmaas/commit/8c81d0fbdf0c4d927fc6f31a1a7cd538345fe9a7))

* add unit tests for logger module ([`8ebe2ca`](https://github.com/RedHatInsights/vmaas/commit/8ebe2ca21c3132ce648a7377682c4a1ae79bdb51))

* add method to write to stderr ([`c19a1b3`](https://github.com/RedHatInsights/vmaas/commit/c19a1b353096efafc9f0ce5f335187690bf50b04))

* remove unused EnumerateLogger ([`c3fe61f`](https://github.com/RedHatInsights/vmaas/commit/c3fe61f3209294e7fc04ffae46fa8a23f824f8f5))

* add missing docstrings ([`c7ef88d`](https://github.com/RedHatInsights/vmaas/commit/c7ef88d16b003e574b493bdf13f5d18d4aeb18da))

* fixing pylint issues in main executable ([`df09c29`](https://github.com/RedHatInsights/vmaas/commit/df09c29c7013d61c529c77ada918633517d0d11c))

* increase max line length ([`33ecf3c`](https://github.com/RedHatInsights/vmaas/commit/33ecf3cdd10539d75da9dfb8221312a778cf5ecd))

* generate pylintrc file

pylint --generate-rcfile &gt; pylintrc

pylint-1.7.4-1.fc27.noarch ([`d1ce64f`](https://github.com/RedHatInsights/vmaas/commit/d1ce64f0b70fbb79b016687abc92af74a02be58d))

* add travis.yml, run pylint and summarize return code

run tests for reposcan on different Python versions ([`9ced3b9`](https://github.com/RedHatInsights/vmaas/commit/9ced3b924c02e20abd6df15e4caa461ce137eb12))

* silence psql retries

fixing
vmaas_reposcan | psql: could not connect to server: Connection refused
vmaas_webapp | psql: could not connect to server: Connection refused ([`77a54a0`](https://github.com/RedHatInsights/vmaas/commit/77a54a0af59c89102d3e47a2ee29711359c67df3))

* wait for PostgreSQL in webapp ([`2631da3`](https://github.com/RedHatInsights/vmaas/commit/2631da37028512a674cf08862169b4e4522a59c2))

* wait for PostgreSQL in reposcan ([`bd65e29`](https://github.com/RedHatInsights/vmaas/commit/bd65e299f8cfcb29885a03a6a18aa772a9b4d4f2))

* sync repositories at once ([`66027e1`](https://github.com/RedHatInsights/vmaas/commit/66027e1dbb0e209d297e51e7943ae97a19b1c400))

* api: fix way of passing input data in POST request ([`fb625c5`](https://github.com/RedHatInsights/vmaas/commit/fb625c539ec5b683a07ab537a90a43ce8893bcf8))

* fix duplicate results caused by joined CVE table ([`9675b4e`](https://github.com/RedHatInsights/vmaas/commit/9675b4e3240b5852bfddd963b8ea3231cbe17b0c))

* api: add package list to response in JSON format. ([`e159440`](https://github.com/RedHatInsights/vmaas/commit/e1594403bfcabafbecaacebe02343204e07e9cdd))

* check if repository is already synced ([`41d5cb1`](https://github.com/RedHatInsights/vmaas/commit/41d5cb1e384158c80a31a0c57d77e53de7755fe6))

* fixup! update doc with docker-compose startup instructions ([`4bb7a60`](https://github.com/RedHatInsights/vmaas/commit/4bb7a604020ecbe09172963d6ac37c0124143345))

* update doc with docker-compose startup instructions ([`cc722e1`](https://github.com/RedHatInsights/vmaas/commit/cc722e1a77541e4720b97b03b683f4f16bae962d))

* moved database settings into shared env file ([`366ad53`](https://github.com/RedHatInsights/vmaas/commit/366ad53348dcc8818c35ef53b60f1b430b6b3ad6))

* docker compose file to start all containers at once ([`e4fac79`](https://github.com/RedHatInsights/vmaas/commit/e4fac793c664cc4e0baef5e69880b77671b36f1b))

* add product ID column ([`950e1bf`](https://github.com/RedHatInsights/vmaas/commit/950e1bf2c39008bbe4a0b2dfcf5dc3b93be286e5))

* api: add handler for json input. ([`11348b3`](https://github.com/RedHatInsights/vmaas/commit/11348b3ac4db4a1c30e9eefc744845c2bd4a15a7))

* add more messages ([`a1dc0ea`](https://github.com/RedHatInsights/vmaas/commit/a1dc0ea7135e92c35287ebf9ac42725dfad0a87e))

* move load and unload methods inside repository class ([`23b55b3`](https://github.com/RedHatInsights/vmaas/commit/23b55b35d0ce4c65d9c99433fd8f84e17a9e8eeb))

* download all repomd files at once and then create batches for further steps

and further checks for repository.repomd attribute are not needed ([`b6ff21f`](https://github.com/RedHatInsights/vmaas/commit/b6ff21f67af1b071776b3eebd960ba0520f6ffee))

* after repomd download, skip further processing of repositories with older/current timestamp ([`f648b03`](https://github.com/RedHatInsights/vmaas/commit/f648b03530951abdd7e9fae4af0205741a717696))

* run dummy_crawler in infinite loop. ([`6b7e166`](https://github.com/RedHatInsights/vmaas/commit/6b7e16608ac81ef85d294d2caa1fe7685fd9bd46))

* name column is currently used for repository url

save url in url column and in future name should contain some shorter identifier - defined by user or pulp repo label etc. ([`d421130`](https://github.com/RedHatInsights/vmaas/commit/d4211302fbfc577fc2d17b18e0259f50c9fca66c))

* add column to store timestamp of repositories ([`d2faad3`](https://github.com/RedHatInsights/vmaas/commit/d2faad35ff2f1d001be8f08df65527590de0e1f1))

* add unification with other services to instructions. ([`d90d6b1`](https://github.com/RedHatInsights/vmaas/commit/d90d6b1f2e4eece3d371ba4a67b16e7d94386f98))

* add an entypoint for reposcan container, remove unnecessary files. ([`51597e8`](https://github.com/RedHatInsights/vmaas/commit/51597e827624df79b799216803bedd47d9f42244))

* remove confusing between image name and container name for the database service. ([`8cf1b94`](https://github.com/RedHatInsights/vmaas/commit/8cf1b945af9c42cade79bf9333e755007e995d8b))

* add instruction in README file. ([`b44faa6`](https://github.com/RedHatInsights/vmaas/commit/b44faa633461570883bc3918ea934ea25c6f6a7b))

* API service reads database credentials from environment variables. ([`b04f3ff`](https://github.com/RedHatInsights/vmaas/commit/b04f3ff213de94e8b8d2427fb04ab9432446f040))

* add changes to the API service Dockerfile:

1. add environment variables
2. add autostart of the application
3. fix problem with epel-release repository installation &amp; python libs installation ([`840959b`](https://github.com/RedHatInsights/vmaas/commit/840959bb7e85a1b7b9cedc0699af82b0ab1851f8))

* make sure all texts inside XML elements are stripped

e.g. updateinfo in /content/dist/rhel/rhui/server/6/6Server/x86_64/rhscl/1/os repository contains trailing whitespaces ([`c50baae`](https://github.com/RedHatInsights/vmaas/commit/c50baaee6a11e4503d5ccb01d9f7fceb84bde298))

* unify sha and sha1 types ([`f72fcef`](https://github.com/RedHatInsights/vmaas/commit/f72fcef65e11f30d32b31bea313848164d004f6c))

* summary and rights fields can be undefined

e.g. https://access.redhat.com/errata/RHBA-2006:0155 ([`696fd41`](https://github.com/RedHatInsights/vmaas/commit/696fd415907a21a9e3f21c952337b9c9b8e19ecb))

* detect failed downloads, save status code in DownloadItem

continue with repository processing only if repomd was successfully downloaded ([`50a4737`](https://github.com/RedHatInsights/vmaas/commit/50a4737ea539ddb4f6e4aee4fa5cc5b8dcdc7f27))

* prevent duplicated insert when some package is specified multiple times in metadata

e.g. dnsmasq-utils-2.76-2.el7_4.2.x86_64 in repo content/aus/rhel/server/7/7.4/x86_64/optional/os/ ([`aa0a9a1`](https://github.com/RedHatInsights/vmaas/commit/aa0a9a1698210f98150fffec4913e8593a8eaf62))

* be able to reuse unpacker queue in second batch ([`8a4ff1f`](https://github.com/RedHatInsights/vmaas/commit/8a4ff1f745956089189a5eb1f2b849eeaac14254))

* download and import repositories in batches ([`72ad339`](https://github.com/RedHatInsights/vmaas/commit/72ad33920e7245799ac7e166358a051a346bd197))

* support reading repos from file ([`3ec75bb`](https://github.com/RedHatInsights/vmaas/commit/3ec75bb027f4b4ae6965e04e922943e35d532fcc))

* make sure unique data are imported when single CVE is specified multiple times

e.g. https://access.redhat.com/errata/RHSA-2005:802 ([`46429de`](https://github.com/RedHatInsights/vmaas/commit/46429de26b527c5b0bbc605004fe92cdebe93ffc))

* description field can be undefined

e.g. https://access.redhat.com/errata/RHEA-2003:018 ([`514fece`](https://github.com/RedHatInsights/vmaas/commit/514fecebcb5855b1c3546b3fb972c82707e1f413))

* fixing inaccurate variable name ([`1eab0bc`](https://github.com/RedHatInsights/vmaas/commit/1eab0bc7444b7af9f1d84f33e3b8183f1225bef4))

* ignore files from JB IDEs ([`93489cd`](https://github.com/RedHatInsights/vmaas/commit/93489cdd8cd96d987d8b05e5eac3e5835c668b59))

* fix sync of repository without packages ([`637a213`](https://github.com/RedHatInsights/vmaas/commit/637a2135e6d5a63cb94d8a87292d3217f6fc5156))

* add simple Docker file to make an image of vmaas webapp.

The application is not running after container is started. Need to run it manually. ([`91e99c8`](https://github.com/RedHatInsights/vmaas/commit/91e99c8e56f0338db34788838d161319971e87ab))

* add python tornado script to serve requests.

This script is just a wrapper under errata.py which makes requests to Database. ([`381cbb0`](https://github.com/RedHatInsights/vmaas/commit/381cbb019b9dce31de5a2f18e0701a065e7d96c1))

* add dummy crawler.

The real crawler will crawl via Red Hat CDN, download and parse repodata.
For now, I just add a predefined list of repositories. ([`dc0525d`](https://github.com/RedHatInsights/vmaas/commit/dc0525dbe97caa4fcd40eee0a335846f8a493292))

* add PoC algorithm adapted to schema ([`bd40c2f`](https://github.com/RedHatInsights/vmaas/commit/bd40c2f9d87db0d9fc365d96719710e3014697d3))

* fixed typo in command example ([`5b0efec`](https://github.com/RedHatInsights/vmaas/commit/5b0efec5c1276506073936451b0de382d971f1de))

* container build &amp; use instructions ([`3ad07c4`](https://github.com/RedHatInsights/vmaas/commit/3ad07c4de38f796f6756791100dbbd434b228eeb))

* Dockerfile for reposcan service ([`15e364e`](https://github.com/RedHatInsights/vmaas/commit/15e364ea7bc9de338f9e272a3bf1b82b6f3cf0ba))

* add readme ([`1dd4b58`](https://github.com/RedHatInsights/vmaas/commit/1dd4b58f7e0c55cb4224a6e124ec37e6137c133f))

* add code to store repository in DB ([`968b9c8`](https://github.com/RedHatInsights/vmaas/commit/968b9c8ab0b6fcea78cf0523840f006397507c90))

* move repository handling code to RepositoryController ([`f4a933b`](https://github.com/RedHatInsights/vmaas/commit/f4a933bfe5796339d031e26811107045b906db1e))

* support primary_db ([`31892b0`](https://github.com/RedHatInsights/vmaas/commit/31892b071a581e61155c56727690d266b7039d42))

* wrap parsed metadata into Repository class ([`eaca292`](https://github.com/RedHatInsights/vmaas/commit/eaca2928affca8539412a555e093e9513b87530a))

* support parsing updateinfo ([`afa5a7f`](https://github.com/RedHatInsights/vmaas/commit/afa5a7fc68222a650b75a82099d776bf9ac1d4cd))

* support parsing primary ([`be032f9`](https://github.com/RedHatInsights/vmaas/commit/be032f95a2d6691cb038431ef4ba766de9462354))

* add archive unpacker ([`ac0c3f4`](https://github.com/RedHatInsights/vmaas/commit/ac0c3f4de4de5f7308c0a9d095091eeaef1a86aa))

* add repomd unit test ([`1b8e281`](https://github.com/RedHatInsights/vmaas/commit/1b8e28167276d0ce0d5fbb7e9797d198e3023d77))

* adding code to download repodata and parse downloaded repomd file ([`80d1b3c`](https://github.com/RedHatInsights/vmaas/commit/80d1b3c63a62b60668be770642e4f5a222da14c8))

* update README for database service. ([`c5e9657`](https://github.com/RedHatInsights/vmaas/commit/c5e96573974fbd0bdaaf1e892d6bc763fd6e8165))

* add table errata_repo ([`2dda4d8`](https://github.com/RedHatInsights/vmaas/commit/2dda4d88a2d4e23dfcbafacd4b0f3a1c0dbaeb38))

* use TEXT types instead of VARCHAR ([`feccdf9`](https://github.com/RedHatInsights/vmaas/commit/feccdf9718652dd16de52606716ed55d95375090))

* add Dockerfile for the database microservice.

It uses default PostgreSQL image from docker hub https://hub.docker.com/_/postgres/ ([`ef37f11`](https://github.com/RedHatInsights/vmaas/commit/ef37f11333cfdd451ca7cae6a88d0533c830b77a))

* use NUMERIC instead of INT

vmaas=&gt; select rpmver_array(&#39;3.6.0.v20120721114722&#39;);
ERROR:  integer out of range
CONTEXT:  PL/pgSQL function rpmver_array(character varying) line 52 at assignment ([`1053c94`](https://github.com/RedHatInsights/vmaas/commit/1053c9429ea4e8eb6b442a60e196d18820d9a0ce))

* add missing package arch attribute ([`04eb935`](https://github.com/RedHatInsights/vmaas/commit/04eb935e02e3c5c035bbc00f09bf69e067c77980))

* add unique constraints

make checksum type name unique
make evr columns unique
make package columns unique
make repo name unique
make pkg_repo columns unique
make pkg_errata columns unique
make cve name unique
make errata_cve columns unique ([`59670ec`](https://github.com/RedHatInsights/vmaas/commit/59670ec8ca34394e02fc6ff351d076c7a24852e0))

* resize columns

package name column is not big enough
errata synopsis column is not big enough ([`bd14442`](https://github.com/RedHatInsights/vmaas/commit/bd144426340495ff6798156d9699046d84985f02))

* make sure evr column is not null ([`be98954`](https://github.com/RedHatInsights/vmaas/commit/be989541606c285927a5af6c4751f0223c5e54cb))

* rename db directory. ([`55863b2`](https://github.com/RedHatInsights/vmaas/commit/55863b2517036ddef8d0e14f2448970b2f02658d))

* these functions are defined in current schema, not in rpm schema ([`d3f07c7`](https://github.com/RedHatInsights/vmaas/commit/d3f07c7238e67012b6d30c173235dc19786de3db))

* add DB schema creation script. ([`f9b3038`](https://github.com/RedHatInsights/vmaas/commit/f9b30380d9c9f7d6099d70a4400f5e6b21f33dfa))

* Initial commit ([`7d5fd98`](https://github.com/RedHatInsights/vmaas/commit/7d5fd9813a08f6b05003da2c99e7df3715b039e8))
