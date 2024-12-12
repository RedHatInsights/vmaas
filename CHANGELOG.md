# CHANGELOG


## v2.69.25 (2024-12-12)

### Chores

- **deps**: Update grafana/grafana docker tag to v11.4.0
  ([`343c585`](https://github.com/RedHatInsights/vmaas/commit/343c585960e6e23b23d49a7ad29924f0d87736aa))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.24 (2024-12-06)

### Chores

- Upgrade python version
  ([`0da3d3f`](https://github.com/RedHatInsights/vmaas/commit/0da3d3f08e4fe6b3521c174a89d50d07797476e5))

RHINENG-14727

RHINENG-14647

RHINENG-14648


## v2.69.23 (2024-12-05)

### Chores

- **deps**: Update grafana/grafana docker tag to v11.3.1
  ([`7a5e88b`](https://github.com/RedHatInsights/vmaas/commit/7a5e88be614fc6a236467b385d4b5186005271a4))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.22 (2024-12-04)

### Bug Fixes

- False positives for kernel-rt source package
  ([`9f4919d`](https://github.com/RedHatInsights/vmaas/commit/9f4919dc6e33a996bb03dfe083abcf11ff825589))

RHINENG-14565


## v2.69.21 (2024-11-30)

### Chores

- **deps**: Update konflux references
  ([`0996858`](https://github.com/RedHatInsights/vmaas/commit/09968585809b075315bbfddb5c6cbe67f95162c2))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.20 (2024-11-28)

### Bug Fixes

- Ignore updates from rhel-alt el7a release
  ([`2f409ef`](https://github.com/RedHatInsights/vmaas/commit/2f409efc4d34fedfc3ac3d43f7f98beb46d9781f))

RHINENG-14561


## v2.69.19 (2024-11-23)

### Chores

- **deps**: Update konflux references
  ([`3ba185b`](https://github.com/RedHatInsights/vmaas/commit/3ba185b6d99d1eb716c781ce8547d1bd31bed767))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.18 (2024-11-19)

### Chores

- **deps**: Update grafana/grafana docker tag to v11.3.0
  ([`0322625`](https://github.com/RedHatInsights/vmaas/commit/032262589e51e4c517397d1ba4cf6e668736c622))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.17 (2024-11-19)

### Chores

- Solve issues reported by grype
  ([`909b997`](https://github.com/RedHatInsights/vmaas/commit/909b997801b3fcdf2252002af769aca3bd37f76c))

update dependencies

remove /vmaas/go/pkg/mod/github.com/gabriel-vasile/mimetype\@v1.4.6/testdata which contains
  vulnerable files RHINENG-14310


## v2.69.16 (2024-11-18)

### Chores

- **deps**: Update konflux references
  ([`015966b`](https://github.com/RedHatInsights/vmaas/commit/015966bcbde103e3b8e53fb2b387e07afa968297))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.15 (2024-11-14)

### Continuous Integration

- Revert image temporarily until konflux is stable enough
  ([`70d3301`](https://github.com/RedHatInsights/vmaas/commit/70d330112ecb4556d27c83644cdcd05290164aef))


## v2.69.14 (2024-11-12)

### Chores

- **deps**: Update konflux references
  ([`4f0ff17`](https://github.com/RedHatInsights/vmaas/commit/4f0ff17420eaa91dba39119728b0d46008c9019b))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.13 (2024-11-12)

### Chores

- Update dependencies
  ([`1000eba`](https://github.com/RedHatInsights/vmaas/commit/1000eba36e6f1062f6db657c21f9954d171985ae))

fix possible werkzeug vulnerabilities

RHINENG-14310


## v2.69.12 (2024-11-11)

### Continuous Integration

- Create renovate PRs only weekly
  ([`7c8031d`](https://github.com/RedHatInsights/vmaas/commit/7c8031d5f3f25edf604d32a42ba27726ede2d6a6))


## v2.69.11 (2024-11-06)

### Continuous Integration

- Add new mandatory RPM signature scan task to tekton
  ([`5c2053b`](https://github.com/RedHatInsights/vmaas/commit/5c2053b065c0a2fcb93783945ea761686617a8fd))


## v2.69.10 (2024-11-02)

### Chores

- **deps**: Update konflux references
  ([`26b7cb9`](https://github.com/RedHatInsights/vmaas/commit/26b7cb9e8948d1aab77812463968e7bea9542bcb))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.9 (2024-10-29)

### Bug Fixes

- **s3**: Get accessKey from bucket not objectStore
  ([`d42dfaf`](https://github.com/RedHatInsights/vmaas/commit/d42dfaf0a6d559316c06d3c00ec5d2c7d192a611))


## v2.69.8 (2024-10-29)

### Chores

- **deps**: Update konflux references
  ([`7923c3a`](https://github.com/RedHatInsights/vmaas/commit/7923c3ae3a4676abb93a0525455ed486602d8cac))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.7 (2024-10-25)

### Bug Fixes

- **webapp**: Label key is not in result dict if all repos are skipped
  ([`d45a9a8`](https://github.com/RedHatInsights/vmaas/commit/d45a9a80c9f3118db66db3d686f840c0a3c2547f))

causing KeyError


## v2.69.6 (2024-10-25)

### Chores

- Revert to ubi8
  ([`2951dc4`](https://github.com/RedHatInsights/vmaas/commit/2951dc4f6afb2afde5b806ef58ac24b1bf5fe122))

RHINENG-13902


## v2.69.5 (2024-10-24)

### Chores

- **deps**: Update konflux references
  ([`c1415b3`](https://github.com/RedHatInsights/vmaas/commit/c1415b3ca283a42318d8e526f6afe18d90991c61))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.4 (2024-10-21)

### Chores

- **deps**: Update konflux references
  ([`79e50c9`](https://github.com/RedHatInsights/vmaas/commit/79e50c9f2f9f49f6824af8bfb6bc3732cd945508))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.3 (2024-10-17)

### Chores

- **deps**: Update konflux references to 67f0290
  ([`7b3adfc`](https://github.com/RedHatInsights/vmaas/commit/7b3adfcbfc56a5c3a75625a914d00f25baa0bdf5))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.69.2 (2024-10-17)

### Chores

- Intenral api to upload dump to s3
  ([`6637c3e`](https://github.com/RedHatInsights/vmaas/commit/6637c3e1d537b9e46c778e404833ba550f9e1c58))

RHINENG-13599


## v2.69.1 (2024-10-17)

### Chores

- Upgrade db to pg 16
  ([`9a0a14e`](https://github.com/RedHatInsights/vmaas/commit/9a0a14e78f6f822cbd7c0b90a880d4fb560ed920))

RHINENG-13735


## v2.69.0 (2024-10-17)

### Features

- Upload compressed sqlite dump to s3
  ([`3c04002`](https://github.com/RedHatInsights/vmaas/commit/3c04002967063fdd9240a2e243f1d80b520554b1))

RHINENG-13599

- **dump**: Deploy app with object store
  ([`497f005`](https://github.com/RedHatInsights/vmaas/commit/497f005320e14681620da135f075ec363a477ec9))

RHINENG-13599


## v2.68.3 (2024-10-16)

### Chores

- Update libs (mainly starlette vulnerability)
  ([`b6c56b8`](https://github.com/RedHatInsights/vmaas/commit/b6c56b86c8789f37893231c6b7e395ecef2848dd))

### Continuous Integration

- Pylint too-many-positional-arguments
  ([`cb3a7f5`](https://github.com/RedHatInsights/vmaas/commit/cb3a7f5ed87aeda1a27e778350fd1e784f55e46f))


## v2.68.2 (2024-10-16)

### Continuous Integration

- Only build tagged commits
  ([`3613405`](https://github.com/RedHatInsights/vmaas/commit/361340577c03de14e41bbaec6eb22ba9de2c66ae))


## v2.68.1 (2024-10-16)

### Chores

- **deps**: Update konflux references
  ([`f0a8622`](https://github.com/RedHatInsights/vmaas/commit/f0a86223e22137a9c830d93a7b18dcfe071324c6))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.68.0 (2024-10-15)

### Bug Fixes

- Env var to disable newer release version updates
  ([`1513a35`](https://github.com/RedHatInsights/vmaas/commit/1513a358de1b895c8521649e5ba87f1a0eb99a65))

RHINENG-13676

RHINENG-4854

### Features

- Remove use_csaf from request
  ([`50420e9`](https://github.com/RedHatInsights/vmaas/commit/50420e93c0de8622b3abf16eb31ea791a662fa3d))

RHINENG-7872


## v2.67.4 (2024-10-14)

### Chores

- **deps**: Update konflux references to 674e70f
  ([`71cc9be`](https://github.com/RedHatInsights/vmaas/commit/71cc9be1d8171588fe983daa6584e77eef7e4ba9))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.67.3 (2024-10-14)

### Chores

- **deps**: Update konflux references
  ([`e6c733c`](https://github.com/RedHatInsights/vmaas/commit/e6c733c213336612c859bca5529265e4b6e47500))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.67.2 (2024-10-11)

### Chores

- **deps**: Update konflux references to 7a92ef9
  ([`962f040`](https://github.com/RedHatInsights/vmaas/commit/962f04022bde6a76f6fddfc1b30fbbc0198d3de1))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.67.1 (2024-10-08)

### Chores

- **deps**: Update konflux references to 37b9187
  ([`d1ddfd7`](https://github.com/RedHatInsights/vmaas/commit/d1ddfd718a5cba587f110948370f67e7c8986344))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>

### Continuous Integration

- Create patch tag for more keywords
  ([`9417984`](https://github.com/RedHatInsights/vmaas/commit/94179846e306dd8ac9ee21d316b0420911520263))

going to enable Konflux image build only for tags


## v2.67.0 (2024-10-07)

### Chores

- Trigger stage deployment
  ([`e5984d3`](https://github.com/RedHatInsights/vmaas/commit/e5984d351ad4aece2ddb5aee0d28bf0c89ca9644))

- **deps**: Update grafana/grafana docker tag to v11.2.2
  ([`a351d4a`](https://github.com/RedHatInsights/vmaas/commit/a351d4a726e70886dbf2b1cfadbcdf1e89389dcf))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>

- **test**: Cache contains less variables
  ([`c1e26ca`](https://github.com/RedHatInsights/vmaas/commit/c1e26caa6aa7ee4cb34282371af6d59985e19da3))

RHINENG-7872

### Features

- Drop oval tables
  ([`382bae7`](https://github.com/RedHatInsights/vmaas/commit/382bae705601d5f58190c2505e6d137e9bbb4e92))

RHINENG-7872

- Remove oval download,parse,store
  ([`18acfe6`](https://github.com/RedHatInsights/vmaas/commit/18acfe6f20347ba1ff0acde8e939425b7f305f20))

RHINENG-7872

- Remove oval env variables
  ([`6c860bf`](https://github.com/RedHatInsights/vmaas/commit/6c860bfb244dd9d4e95df661e5b262a5ce5abc61))

RHINENG-7872

- Remove oval export
  ([`a6f5ba7`](https://github.com/RedHatInsights/vmaas/commit/a6f5ba7a1d9a032c7ea4e9a2a341599b7dd95b94))

RHINENG-7872

- Remove oval from webapp
  ([`383d28b`](https://github.com/RedHatInsights/vmaas/commit/383d28b271bfb6422d41063674c144f0fed0a5aa))

RHINENG-7872

- Remove oval reposcan api
  ([`0110356`](https://github.com/RedHatInsights/vmaas/commit/0110356d1f8ff8e2466b2608b550d06b2e8ad570))

RHINENG-7872


## v2.66.1 (2024-10-01)

### Bug Fixes

- **vmaas-go**: Revert appendUniq due to performance hit
  ([`c9a2306`](https://github.com/RedHatInsights/vmaas/commit/c9a23060dbeed0881d9026b8207520f61b3c7b51))


## v2.66.0 (2024-10-01)

### Chores

- Increase ecosystem-cert-preflight-checks resources
  ([`6e35316`](https://github.com/RedHatInsights/vmaas/commit/6e35316c71908b1240a603026b84e4e41d056394))

- Konflux image url
  ([`9e784a7`](https://github.com/RedHatInsights/vmaas/commit/9e784a781ec358280fa4c8002fa2c928aa299c42))

### Features

- Remove oval in webapp-go
  ([`e3cb099`](https://github.com/RedHatInsights/vmaas/commit/e3cb099a038260a133c245291e500cca6b99b3f0))

RHINENG-7872


## v2.65.1 (2024-09-30)

### Bug Fixes

- **webapp-go**: Duplicate affected packages and incorrect manually fixable errata
  ([`f96f316`](https://github.com/RedHatInsights/vmaas/commit/f96f31620e2bd71a9b9e68f53db5ad55bd2aeaeb))

### Chores

- Add schema spec
  ([`91c419d`](https://github.com/RedHatInsights/vmaas/commit/91c419ddb708b713d075a61e99a0231901a60318))

- Try to add additional automerge params
  ([`9a1e217`](https://github.com/RedHatInsights/vmaas/commit/9a1e217b5ee0d96c6cf186174350e60321ac0427))

- Try to automerge updating tekton references
  ([`be501df`](https://github.com/RedHatInsights/vmaas/commit/be501df46c61a2acf309c3cc4b9fc5dbb64073f3))

- **deps**: Update grafana/grafana docker tag to v11.2.1
  ([`cb28a4d`](https://github.com/RedHatInsights/vmaas/commit/cb28a4d6e72a8337b87d2ec0121bd73b434ba83c))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>

- **deps**: Update konflux references
  ([`3cdba17`](https://github.com/RedHatInsights/vmaas/commit/3cdba1795ddd6e39460b8db531dbdefbf1e992b2))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.65.0 (2024-09-25)

### Features

- **webapp-go**: Get newer EUS manually fixable from repos
  ([`d9f8e89`](https://github.com/RedHatInsights/vmaas/commit/d9f8e898669990b04a22eb994106e8c150a549cb))


## v2.64.3 (2024-09-25)

### Bug Fixes

- Skip cves missing in mapping
  ([`d1c478f`](https://github.com/RedHatInsights/vmaas/commit/d1c478f603a49b1d149848fda535dc78e0c9ebc2))

RHINENG-12773


## v2.64.2 (2024-09-25)

### Bug Fixes

- Remove removed csaf files from db
  ([`617fe70`](https://github.com/RedHatInsights/vmaas/commit/617fe70ef7c82904fbd8f8333621b9e9574223a8))

RHINENG-12773

### Chores

- Update dependencies
  ([`24b9f05`](https://github.com/RedHatInsights/vmaas/commit/24b9f050877d35df6d58ad557c98ca1506921203))

RHINENG-12514

- Use ubi9
  ([`7b783e5`](https://github.com/RedHatInsights/vmaas/commit/7b783e5c8f580cd450af96f4ea7589633a84917e))

RHINENG-12543

RHINENG-12556

- **deps**: Update grafana/grafana docker tag to v11
  ([`68130f4`](https://github.com/RedHatInsights/vmaas/commit/68130f44c429f4cb5ea2188b97a19a2e1104b1b7))

Signed-off-by: red-hat-konflux <126015336+red-hat-konflux[bot]@users.noreply.github.com>


## v2.64.1 (2024-09-18)

### Bug Fixes

- **webapp**: Don't show repositories without changed packages
  ([`fe87412`](https://github.com/RedHatInsights/vmaas/commit/fe87412522f3e025af5ddc1f2d8e32f4522781c1))

repository may be re-generated but no RPM erratum added (push of container images triggers RPM
  repodata re-generation)

### Chores

- **ephemeral**: Remove --no-remove-resources
  ([`68e9d39`](https://github.com/RedHatInsights/vmaas/commit/68e9d39799b96b869c5bc46c21778a5322245b68))

RHINENG-11573


## v2.64.0 (2024-09-03)

### Chores

- Don't initialize clowder config with init
  ([`8e4cee2`](https://github.com/RedHatInsights/vmaas/commit/8e4cee2d139f14e912d1437f03d188f19bd16d5a))

- **test**: Add vmaas-go tests
  ([`42fd879`](https://github.com/RedHatInsights/vmaas/commit/42fd879867919280b08c6206efa68268d138231f))

### Features

- **csaf**: Use csaf evaluation by default
  ([`39c28fe`](https://github.com/RedHatInsights/vmaas/commit/39c28fe9dbe53effe6746508bcf039149103e448))

RHINENG-7871


## v2.63.1 (2024-08-30)

### Bug Fixes

- **csaf**: Duplicate cpes while processing
  ([`1d8a2c4`](https://github.com/RedHatInsights/vmaas/commit/1d8a2c4f33024e75148d6893979bd653d47aca63))

RHINENG-12112


## v2.63.0 (2024-08-23)

### Chores

- Update gh actions
  ([`7a6b6c6`](https://github.com/RedHatInsights/vmaas/commit/7a6b6c6dc27f4dddc1e01525d78e0b718b43d528))

### Features

- **csaf**: Exclude kernel-alt from evaluation
  ([`3b31812`](https://github.com/RedHatInsights/vmaas/commit/3b318126a14a59f72d2f552ef2f08cc800a80160))

https://github.com/RedHatInsights/vmaas-lib/pull/66

RHINENG-12093


## v2.62.7 (2024-08-09)

### Bug Fixes

- **csaf**: Fixed products with moduels
  ([`2ae057c`](https://github.com/RedHatInsights/vmaas/commit/2ae057c4b9a6514c03b656ae0523ecbc5d49b510))

RHINENG-11156

### Chores

- **pprof**: Profile cpu for 20s
  ([`dbb6b10`](https://github.com/RedHatInsights/vmaas/commit/dbb6b10561c2ab8d6c51689017833d1a723cb869))

use 20s profile instead of default 30s, 3scale timeout in stage/prod is 30s and profile would result
  in gateway timeout


## v2.62.6 (2024-08-08)

### Bug Fixes

- **csaf**: Update indexes for fixed products
  ([`620d218`](https://github.com/RedHatInsights/vmaas/commit/620d21855409d6320bfa6dae6478a4c8c6bec544))

package_name_id is always stored (RHINENG-10310)

RHINENG-11156


## v2.62.5 (2024-08-07)

### Bug Fixes

- **csaf**: Module parsing
  ([`c5a197f`](https://github.com/RedHatInsights/vmaas/commit/c5a197fffc4014ad3f244c7d69431f1ad54efa78))

- don't use purl for unfixed cves - use module product to get module of fixed product

RHINENG-11803 RHINENG-11156

### Chores

- **csaf**: Rename variable including fixed cves
  ([`2970df5`](https://github.com/RedHatInsights/vmaas/commit/2970df5924ad8c98201145232d35dc460a5a2e78))


## v2.62.4 (2024-07-25)

### Bug Fixes

- Add internal endpoint for profiling webapp-go
  ([`451d8c2`](https://github.com/RedHatInsights/vmaas/commit/451d8c2971967458dfec1a91c7b535a298bf8a7b))

RHINENG-11507


## v2.62.3 (2024-07-23)

### Bug Fixes

- Update dependencies
  ([`b143604`](https://github.com/RedHatInsights/vmaas/commit/b143604914fdb1ba8264fe0795eb7017e1591c41))

RHINENG-11425


## v2.62.2 (2024-07-23)

### Bug Fixes

- Stop using beta vex files
  ([`3c34f7b`](https://github.com/RedHatInsights/vmaas/commit/3c34f7bf103c9bea8c966ddb6a43a87328a0f667))

RHINENG-11599


## v2.62.1 (2024-07-04)

### Bug Fixes

- Detect all affected packages for unfixed vulns
  ([`052b781`](https://github.com/RedHatInsights/vmaas/commit/052b781c4e8390c869ad9bf2f348fdb20b6b7549))

RHINENG-11201


## v2.62.0 (2024-07-02)

### Features

- **webapp-go**: Report module info for unfixed CVEs
  ([`ec1ca01`](https://github.com/RedHatInsights/vmaas/commit/ec1ca013b54ab551ef162f97b68499ccadc73a32))

RHINENG-10771


## v2.61.9 (2024-06-27)

### Bug Fixes

- Match cpe pattern substrings
  ([`e3b5f54`](https://github.com/RedHatInsights/vmaas/commit/e3b5f54e6cab5b69950a7cb8d3cbbebd9f8301c9))

RHINENG-10943

### Chores

- Increase webapp memory request/limit
  ([`364f681`](https://github.com/RedHatInsights/vmaas/commit/364f681b374b068e59a772f7335ae347d3764e8a))

- New pylint
  ([`4048e0c`](https://github.com/RedHatInsights/vmaas/commit/4048e0c4d42ea0203880df81c1a2acd6883b7c21))

- Update dependencies
  ([`fda9928`](https://github.com/RedHatInsights/vmaas/commit/fda9928a102f4f944917520bf2631fb9d6d4483d))

RHINENG-10319


## v2.61.8 (2024-06-20)

### Bug Fixes

- **csaf**: Increase default memory request for webapp-go
  ([`a126792`](https://github.com/RedHatInsights/vmaas/commit/a12679247fe67a785a1df6b968388e49444f5b2f))

- **csaf**: Use purl,parse only rpm products
  ([`1623068`](https://github.com/RedHatInsights/vmaas/commit/162306825f829b622e65c20b0ea067dbb5de1c51))

RHINENG-9590


## v2.61.7 (2024-06-20)

### Bug Fixes

- String formatting in CloudWatch
  ([`7d2d84d`](https://github.com/RedHatInsights/vmaas/commit/7d2d84d61e592bee4e79fcc371d9c1e1eca011fa))

RHINENG-8336


## v2.61.6 (2024-06-18)

### Bug Fixes

- **csaf**: Download only files from csv
  ([`423c7a5`](https://github.com/RedHatInsights/vmaas/commit/423c7a5fe2bcbc8e1179e57e2f5ec4bdf5266609))

RHINENG-10605


## v2.61.5 (2024-06-18)

### Bug Fixes

- **reposcan**: Exclude under investigation CVEs from OVAL
  ([`0aa518a`](https://github.com/RedHatInsights/vmaas/commit/0aa518a72210b7da1126a1cf5e6f20970785cb19))

RHINENG-9878


## v2.61.4 (2024-06-13)

### Bug Fixes

- **csaf**: Syntax error with IN query
  ([`37b1e31`](https://github.com/RedHatInsights/vmaas/commit/37b1e31b7ba8de8e0c417065aeb28f958773a2a9))

vmaas-reposcan | vmaas-reposcan 2024-06-03
  17:50:17,781:ERROR:vmaas.reposcan.database.object_store:Failed to import csaf file to DB:
  'Traceback (most recent call last):\n File "/vmaas/vmaas/reposcan/database/csaf_store.py", line
  75, in _save_csaf_files\n cur.execute("select id, name from csaf_file where name in %s",
  (tuple(files),))\npsycopg2.errors.SyntaxError: syntax error at or near ")"\nLINE 1: select id,
  name from csaf_file where name in ()\n ^\n'|

RHINENG-10604

### Chores

- **reposcan**: Add OVAL_SYNC_ALL_FILES flag
  ([`484a105`](https://github.com/RedHatInsights/vmaas/commit/484a105d03007ade05d28ff03062e4eabbd9161a))


## v2.61.3 (2024-06-07)

### Bug Fixes

- **build**: Update it-root-ca
  ([`c1d7cca`](https://github.com/RedHatInsights/vmaas/commit/c1d7ccad297831e22c6944fa1789f72b90e31d1c))

RHINENG-10539


## v2.61.2 (2024-06-06)

### Bug Fixes

- Store package_name_id for fixed csaf_product
  ([`bd09fe2`](https://github.com/RedHatInsights/vmaas/commit/bd09fe25b019f2f75f6efb5e161cf09ea2ec11b1))

RHINENG-10310


## v2.61.1 (2024-06-06)

### Bug Fixes

- Include levelname in CW logs from python code
  ([`eca466c`](https://github.com/RedHatInsights/vmaas/commit/eca466c4c6acfb6ac5bc4fa846499f3dc06a89b7))

RHINENG-8336

### Chores

- Centos 8 Stream was removed, install postgresql and rpm-devel from COPR
  ([`dd006c6`](https://github.com/RedHatInsights/vmaas/commit/dd006c668178412d76d90c8532be56ebd4060831))

- Waive CVE-2019-8341 jinja2 (old CVE, we're using latest version, false positive?)
  ([`d66c1f2`](https://github.com/RedHatInsights/vmaas/commit/d66c1f25ba4e2a846ad0b89fffcfe69aba669cc3))


## v2.61.0 (2024-05-31)

### Bug Fixes

- **csaf**: Start processing fixed product status
  ([`c0a97e9`](https://github.com/RedHatInsights/vmaas/commit/c0a97e92dd6d42cb3fcb4951b30eb848d3cb3c75))

RHINENG-10310

### Chores

- Update go version and dependencies
  ([`42162e2`](https://github.com/RedHatInsights/vmaas/commit/42162e20c20e844f31897380e4ef8e227a9753ba))

RHINENG-9601

- **csaf**: Log warning if there are multiple errata
  ([`7df7880`](https://github.com/RedHatInsights/vmaas/commit/7df7880517a0aa320546312b917cc58aeca5467e))

RHINENG-10310

- **csaf**: Raise NotImplementedError for unsupported status_id
  ([`555b28d`](https://github.com/RedHatInsights/vmaas/commit/555b28d0526ced6221d2f87ab89caf29f8d68ddc))

RHINENG-10310

### Features

- **csaf**: Add errata to db schema
  ([`f6a5a12`](https://github.com/RedHatInsights/vmaas/commit/f6a5a126127621ead0a4b538cf76f5118c65e2e3))

RHINENG-10310

- **csaf**: Dump erratum
  ([`90443d3`](https://github.com/RedHatInsights/vmaas/commit/90443d357d4e082ac94393019c896dae4ff211bf))

RHINENG-10310

- **csaf**: Parse fixed csaf vex products
  ([`6f2580d`](https://github.com/RedHatInsights/vmaas/commit/6f2580d5e6c348d5a6b84296b7e7b94b68628d23))

RHINENG-10310

- **csaf**: Save errata to db
  ([`5450b60`](https://github.com/RedHatInsights/vmaas/commit/5450b6041913977fcf3f62da4fe2d70daab5e610))

RHINENG-10310

### Testing

- **csaf**: Extend test with errata parsing
  ([`572cc41`](https://github.com/RedHatInsights/vmaas/commit/572cc414b683599d38e83af1432a6a4770f634e2))

RHINENG-10310


## v2.60.4 (2024-05-28)

### Bug Fixes

- **csaf**: Cves for source packages
  ([`6b7c3dc`](https://github.com/RedHatInsights/vmaas/commit/6b7c3dc7005fadfe06355cd21a6308388bb848b5))

RHINENG-9890


## v2.60.3 (2024-05-16)

### Bug Fixes

- **csaf**: Remove products if they become fixed/unaffected
  ([`f6b4702`](https://github.com/RedHatInsights/vmaas/commit/f6b470263b6d4af7e30cbc37897a58f7065d6621))

RHINENG-10039


## v2.60.2 (2024-05-16)

### Bug Fixes

- **csaf**: Update file timestamp for skipped cve
  ([`ca43ccc`](https://github.com/RedHatInsights/vmaas/commit/ca43ccc581b707a6889caf48eaa62ff94201478f))

RHINENG-9586

### Chores

- Update dependencies
  ([`79be3aa`](https://github.com/RedHatInsights/vmaas/commit/79be3aa7f551c8e9cfb07250b4ca6bc8d41dd3f6))

RHINENG-10048

- **csaf_test**: Fix input for test_csaf_store
  ([`99d29c2`](https://github.com/RedHatInsights/vmaas/commit/99d29c27075bf19dd401c48e3b4fd0b910f9821f))

use correct CsafData content to call `store` function, this commit is not fixing the test itself
  which does not seem to have any asserts, test just runs the code


## v2.60.1 (2024-04-30)

### Bug Fixes

- Update vmaas-lib to improve concurrency
  ([`112d19c`](https://github.com/RedHatInsights/vmaas/commit/112d19cede5b26978e1e25e9fad0b254f1f6b351))

RHINENG-9798 RHINENG-9797


## v2.60.0 (2024-04-29)

### Features

- **csaf**: Use csaf in /vulnerabilities
  ([`7eb8980`](https://github.com/RedHatInsights/vmaas/commit/7eb8980b6d8866c86dc0cd268f3f42d5da1a5527))

RHINENG-7869


## v2.59.0 (2024-04-25)

### Features

- List modified packages in modified repos
  ([`d9a8181`](https://github.com/RedHatInsights/vmaas/commit/d9a818179e0417ce202d5b4ff21f3853a65fa22a))

RHINENG-9690


## v2.58.4 (2024-04-25)

### Bug Fixes

- **build_deploy**: Only create sc tag when building sc branch
  ([`6b2e818`](https://github.com/RedHatInsights/vmaas/commit/6b2e81844cc4f311daf4eac9306c75007abb8ffb))

### Chores

- Upgrade to latest idna
  ([`3230ca4`](https://github.com/RedHatInsights/vmaas/commit/3230ca4006a71ab85d7d4fe1d3454628af6b0c94))

RHINENG-9574

- **deps**: Bump golang.org/x/net from 0.18.0 to 0.23.0 in /vmaas-go
  ([`c7e6423`](https://github.com/RedHatInsights/vmaas/commit/c7e64233ae9d38fcd12d2850ab205ec5d5ee6547))

Bumps [golang.org/x/net](https://github.com/golang/net) from 0.18.0 to 0.23.0. -
  [Commits](https://github.com/golang/net/compare/v0.18.0...v0.23.0)

--- updated-dependencies: - dependency-name: golang.org/x/net dependency-type: indirect

...

Signed-off-by: dependabot[bot] <support@github.com>


## v2.58.3 (2024-04-17)

### Bug Fixes

- **csaf**: Query argument
  ([`61cae18`](https://github.com/RedHatInsights/vmaas/commit/61cae1881db429a94043db56935190a448b74e1c))

RHINENG-9510


## v2.58.2 (2024-04-17)

### Bug Fixes

- **csaf**: Populate mapping with updated files
  ([`81b4ce6`](https://github.com/RedHatInsights/vmaas/commit/81b4ce627553d1084aa1b4356249de9aa158d9f4))

RHINENG-9510


## v2.58.1 (2024-04-17)

### Bug Fixes

- **reposcan**: Add internal /download/pg_dump api
  ([`92f1f31`](https://github.com/RedHatInsights/vmaas/commit/92f1f3184e292029580ee5eb48476ebfc832442c))

RHINENG-9441


## v2.58.0 (2024-04-11)

### Features

- **csaf**: Load csaf dump in webapp
  ([`770d7ed`](https://github.com/RedHatInsights/vmaas/commit/770d7ed5e78056f062ce4a4e9bc039adc59d9e36))

RHINENG-9212


## v2.57.1 (2024-04-11)

### Bug Fixes

- **csaf**: Improve module parsing from csaf
  ([`17e41dc`](https://github.com/RedHatInsights/vmaas/commit/17e41dc31acedc69675ddba522b5ed9534b39316))

RHINENG-7868

### Chores

- **csaf**: Fix count of files in log
  ([`6807625`](https://github.com/RedHatInsights/vmaas/commit/68076251a9e84a7160058216bc388320ca47b839))


## v2.57.0 (2024-04-04)

### Chores

- Update cryptography package
  ([`c986484`](https://github.com/RedHatInsights/vmaas/commit/c9864849e8b59ac021b677fea8a9baf506faf275))

### Features

- **reposcan**: Add CSAF SQLite dump
  ([`11c8897`](https://github.com/RedHatInsights/vmaas/commit/11c88979f63282bfdc76b88958ce40246ffd6e93))


## v2.56.1 (2024-03-25)

### Bug Fixes

- **csaf**: Don't guess cve name by file name
  ([`6759e29`](https://github.com/RedHatInsights/vmaas/commit/6759e29aeab60134c516765fc21e489ff8276154))

- **csaf**: Extend model with CsafProducts
  ([`5ece339`](https://github.com/RedHatInsights/vmaas/commit/5ece339e5b98a5bdd4d8e0d086cc38133c6cb4bd))

- **csaf**: Finalize db schema
  ([`7fc6a22`](https://github.com/RedHatInsights/vmaas/commit/7fc6a227b0ae94d9c6936c0960c4e87b4ac6a120))

RHINENG-7862

- **csaf**: Handle exceptions when saving files
  ([`e0efcfd`](https://github.com/RedHatInsights/vmaas/commit/e0efcfd4a88ca0ebbe45efc976e727c097afc449))

- **csaf**: Insert missing cpes
  ([`0942fd0`](https://github.com/RedHatInsights/vmaas/commit/0942fd01eebe6beda5c7e14a49fe547e812ecede))

- **csaf**: Modify csaf_store to reflect new schema
  ([`2be4213`](https://github.com/RedHatInsights/vmaas/commit/2be42138f5f249c254eca62a8aaee9e44a7b11ca))

- **csaf**: Store unique products to collection
  ([`31e1e4a`](https://github.com/RedHatInsights/vmaas/commit/31e1e4a8cba3841a7fcd9a6a197b2ba54af4e2eb))

- **csaf**: Update file timestamp after successful cve insert/remove
  ([`2565635`](https://github.com/RedHatInsights/vmaas/commit/25656356bdb5b0ed2ff6e9b4d236f70191b4cd6e))

### Chores

- Ignore CVE-2023-6129 as we're not affected
  ([`45fdf5e`](https://github.com/RedHatInsights/vmaas/commit/45fdf5e0156283cc5f22632295ae09bf19ba471b))

not running on PPC using the lib only for checking expiration dates

- Update protobuf
  ([`b3837dd`](https://github.com/RedHatInsights/vmaas/commit/b3837ddd7e2f34e536986f60efb8822bcd8ba4c4))

- **csaf**: Add csaf_store tests
  ([`edc0943`](https://github.com/RedHatInsights/vmaas/commit/edc0943d72b256c588561d4b00db35a7091f7764))

- **csaf**: Extend model tests
  ([`9218f7a`](https://github.com/RedHatInsights/vmaas/commit/9218f7a8f5f8bffce1d9cb264c69766330c1a309))

- **csaf**: Make sure CVEs are always uppercase
  ([`272b57d`](https://github.com/RedHatInsights/vmaas/commit/272b57d2894984285ccc6407b2cf51a029c9e131))

- **csaf**: Move csaf test data to conftest
  ([`a818921`](https://github.com/RedHatInsights/vmaas/commit/a81892191b31d19e21020870232c7bf224041e61))

- **mypy**: Improve checks and fix issues found by mypy
  ([`404e2ea`](https://github.com/RedHatInsights/vmaas/commit/404e2ea5ef57d7a9bc7578ab48ce1655c68d3c14))

- **tests**: Capture logs in tests
  ([`d88e119`](https://github.com/RedHatInsights/vmaas/commit/d88e119b76e406dd6af4a744ddc021ce2a8c0fb6))


## v2.56.0 (2024-03-06)

### Features

- **reposcan**: Add Csaf Store DB insert
  ([`d73c5ce`](https://github.com/RedHatInsights/vmaas/commit/d73c5ce560683fe12333667455df3dfb850b186a))


## v2.55.1 (2024-02-27)

### Bug Fixes

- **csaf**: Env var to decide what statuses to parse
  ([`8c320fa`](https://github.com/RedHatInsights/vmaas/commit/8c320faf19d4d056d5e766483be2e7e46d62ec07))

RHINENG-8391

- **csaf**: Extend model with product status id
  ([`7517f1d`](https://github.com/RedHatInsights/vmaas/commit/7517f1dde49ac493dad1eba9622d3fa9e5059347))

RHINENG-8391

- **csaf**: Set product status id in parser
  ([`1955002`](https://github.com/RedHatInsights/vmaas/commit/1955002d66980068e3d21bca713483491c86ecb6))

RHINENG-8391


## v2.55.0 (2024-02-22)

### Bug Fixes

- **webapp-go**: Unused variable
  ([`c404a55`](https://github.com/RedHatInsights/vmaas/commit/c404a55e891c118ba595f1e97610a68cd8f3fed7))

### Chores

- **deps**: Update vulnerable dependencies
  ([`7d927cf`](https://github.com/RedHatInsights/vmaas/commit/7d927cf96be934631dda627ab0280665103f2ced))

starlette, python-multipart, and cryptography RHINENG-8390

### Features

- Update vmaas-lib
  ([`589a11f`](https://github.com/RedHatInsights/vmaas/commit/589a11f4cd700876c9a435602e4eee1908c6cc5d))

RHINENG-4854


## v2.54.2 (2024-02-20)

### Bug Fixes

- **ephemeral**: Increase max_stack_depth
  ([`6af693d`](https://github.com/RedHatInsights/vmaas/commit/6af693d140ab73b1a2c6bf5f6a6d1c76b795b9e3))

RHINENG-8335


## v2.54.1 (2024-02-15)

### Bug Fixes

- **metrics**: Log full endpoint in reposcan but only part of it in webapp
  ([`293a3e4`](https://github.com/RedHatInsights/vmaas/commit/293a3e4a70e50439bb0778571c38749c8b4351e3))

to avoid too many metrics in prometheus

- **metrics**: Update grafana dashboard with renamed metrics
  ([`8c4f76d`](https://github.com/RedHatInsights/vmaas/commit/8c4f76decc505f70a2a3f0392646664406400464))

### Chores

- Check reposcan code with mypy, simplify action with container
  ([`27c5aaa`](https://github.com/RedHatInsights/vmaas/commit/27c5aaade286cf72282e2771dbd8caae74b16e52))

RHINENG-7736


## v2.54.0 (2024-01-29)

### Chores

- Don't sync all csaf files by default
  ([`ef41296`](https://github.com/RedHatInsights/vmaas/commit/ef412963d5803bf2a3625ca7a6fe7c336bcf7200))

- Golang.org/x/crypto to >= 0.17.0
  ([`7318287`](https://github.com/RedHatInsights/vmaas/commit/7318287515119780c91c55883e055488c8e097e1))

### Features

- **csaf**: Extend csaf models and fix type hints
  ([`918745c`](https://github.com/RedHatInsights/vmaas/commit/918745c75abc418df20565c240c35af1b4ae4079))

RHINENG-7697

- **csaf**: Parse CSAF JSONs into CsafCves
  ([`b2fccaa`](https://github.com/RedHatInsights/vmaas/commit/b2fccaaf3f4944b051fb8d8ff4c7506dafb4fabe))

RHINENG-7697

### Testing

- **csaf**: Add unit tests for csaf model and parser
  ([`b0c0e11`](https://github.com/RedHatInsights/vmaas/commit/b0c0e119e7c236be70be1e36ce436a7825a6a236))

RHINENG-7697


## v2.53.1 (2024-01-24)

### Bug Fixes

- Implement access log in middleware, allows adding timing info and solves cloudwatch support
  ([`e41fc94`](https://github.com/RedHatInsights/vmaas/commit/e41fc94f39a4a1ec730e32d1db4934193ac2b72d))

- **webapp**: Middlewares should be stateless to work concurrently
  ([`7b4ea6b`](https://github.com/RedHatInsights/vmaas/commit/7b4ea6b41c400e792712de3347ab64d1e0957d31))


## v2.53.0 (2024-01-23)

### Features

- **reposcan**: Add CSAF sync task
  ([`67c24d2`](https://github.com/RedHatInsights/vmaas/commit/67c24d275f01deff6bf44d3ec8c90f804b9ef800))


## v2.52.0 (2024-01-22)

### Chores

- Fix code coverage report
  ([`2e920bc`](https://github.com/RedHatInsights/vmaas/commit/2e920bc333d14bf3b7adea5c38a93be2d8484e74))

RHINENG-7698

- Replace strtobool by custom impl
  ([`0cb451e`](https://github.com/RedHatInsights/vmaas/commit/0cb451e6156e34ebc763f834af47e080e92c8e22))

- Update checkout and setup-python actions
  ([`46f8412`](https://github.com/RedHatInsights/vmaas/commit/46f841209981d75d1617aa8e991eb0820eec9adc))

- Update python version
  ([`2e9b3a3`](https://github.com/RedHatInsights/vmaas/commit/2e9b3a38a89ca2f8457be81963b4f5cec31c9fe9))

RHINENG-7727

### Features

- **csaf**: Add csaf_ tables needed to store csaf data
  ([`96dbd27`](https://github.com/RedHatInsights/vmaas/commit/96dbd278409ca0d35c42073e0cb32a788953a008))

RHINENG-6814

### Refactoring

- Upgrade connexion
  ([`e461019`](https://github.com/RedHatInsights/vmaas/commit/e4610196da13f4966cdea15852da1f4d5b899c59))

remove unsupported aiohttp remove flask replace tornado PeriodicCallback functionality with
  apscheduler install uvicorn as ASGI server

RHINENG-5883

- **reposcan**: Support connexion 3
  ([`560a1a5`](https://github.com/RedHatInsights/vmaas/commit/560a1a5d78ca839a90d018553bff11d78ff93fd2))

use AsyncApp instead of FlaskApp use apscheduler instead of tornado PeriodicCallback

re-factor subprocess handling

RHINENG-5883

- **webapp**: Support connexion 3
  ([`9790f4f`](https://github.com/RedHatInsights/vmaas/commit/9790f4f6b09ba9554835d1d016512c8fe4ce2f68))

use AsyncApp instead of AioHttpApp

RHINENG-5883


## v2.51.0 (2024-01-11)

### Chores

- Add len() for batch_list
  ([`f48fcc1`](https://github.com/RedHatInsights/vmaas/commit/f48fcc1fac255e3f5444db824071b30bfee8b93d))

- **deps**: Add attrs and recreate poetry lock
  ([`ba77d20`](https://github.com/RedHatInsights/vmaas/commit/ba77d206152449b78212ec7fe66eb745f040f25d))

### Features

- **csaf**: Add basic metrics
  ([`5c5175f`](https://github.com/RedHatInsights/vmaas/commit/5c5175f6a30c374500912071614dee851daa69e1))

RHINENG-6813

- **csaf**: Add csaf_file table
  ([`61a2cad`](https://github.com/RedHatInsights/vmaas/commit/61a2cad130bc5437cf8bd263f9e891ced819f9de))

RHINENG-6813

- **csaf**: Add logic for downloading csaf files
  ([`6bb6436`](https://github.com/RedHatInsights/vmaas/commit/6bb6436b0cef071da337c83856c7b5d5ad451790))

RHINENG-6813

- **csaf**: Model collection of csaf files
  ([`121fbe4`](https://github.com/RedHatInsights/vmaas/commit/121fbe45ff14a310005c5cde87104e383b1c303a))

RHINENG-6813

- **csaf**: Module for storing csaf to db
  ([`d0acdc3`](https://github.com/RedHatInsights/vmaas/commit/d0acdc320b329208daa04127d9a7fd2f6f5ed4d8))

RHINENG-6813


## v2.50.4 (2024-01-09)

### Bug Fixes

- Add required apiPath for app-common-go
  ([`d8d4873`](https://github.com/RedHatInsights/vmaas/commit/d8d4873c7d33529c9151bd08dcddd6d49a9fe32f))

vmaas-webapp-go | field apiPath in DependencyEndpoint: required vmaas-webapp-go | panic: runtime
  error: invalid memory address or nil pointer dereference vmaas-webapp-go | [signal SIGSEGV:
  segmentation violation code=0x1 addr=0x8 pc=0xb9bd3c] vmaas-webapp-go | vmaas-webapp-go |
  goroutine 1 [running]: vmaas-webapp-go | github.com/redhatinsights/vmaas/base/utils.initDB()
  vmaas-webapp-go | 	/vmaas/go/src/vmaas/base/utils/config.go:71 +0x2c vmaas-webapp-go |
  github.com/redhatinsights/vmaas/base/utils.init.0() vmaas-webapp-go |
  	/vmaas/go/src/vmaas/base/utils/config.go:63 +0x30 vmaas-webapp-go exited with code 2

### Chores

- Migrate from pipenv to poetry
  ([`6b0fd00`](https://github.com/RedHatInsights/vmaas/commit/6b0fd005149bf8bb187c26136e5c0c963f6f10a8))

- Split github workflow steps in tests job
  ([`8404869`](https://github.com/RedHatInsights/vmaas/commit/84048691c28c0ed1f461661449afe7a7000d59e4))


## v2.50.3 (2023-11-24)

### Bug Fixes

- Update vmaas-lib
  ([`4ea8559`](https://github.com/RedHatInsights/vmaas/commit/4ea855902e2bfa735b2d9d686437023d21d31e4e))


## v2.50.2 (2023-11-23)

### Bug Fixes

- Update go to 1.20 and update dependencies
  ([`0103109`](https://github.com/RedHatInsights/vmaas/commit/0103109781bef103f4c6fc8882ba9fbd65e07261))

go 1.19 is unsupported and go1.20 is already available in ubi8 RHINENG-3785

### Chores

- Remove old cve ignores
  ([`a0872b4`](https://github.com/RedHatInsights/vmaas/commit/a0872b4cd43de7cdd4a7e9ff39a23376119e3bd5))

- Update dependencies
  ([`21e9fce`](https://github.com/RedHatInsights/vmaas/commit/21e9fce724ca013dfb382144a352a43e5dc65e9a))

- Update golang.org/x/net
  ([`216a7a2`](https://github.com/RedHatInsights/vmaas/commit/216a7a2830ddeefc32ca65d367de032badd4ad11))


## v2.50.1 (2023-11-20)

### Bug Fixes

- Use new url for cpe dictionary xml
  ([`310d3cd`](https://github.com/RedHatInsights/vmaas/commit/310d3cd54b7f56c130f2674f493939b99147f2a8))

### Chores

- Temporary ignore vulnerabilities in pipenv
  ([`1871dd3`](https://github.com/RedHatInsights/vmaas/commit/1871dd38e20f76379879e3db4ec8710d9d01573e))


## v2.50.0 (2023-10-19)

### Features

- **webapp**: Return and display latest change of repo in vmaas
  ([`8e483ad`](https://github.com/RedHatInsights/vmaas/commit/8e483adebe852c38e161c7d5c7ba1f4d504ec2a7))

RHINENG-2608


## v2.49.1 (2023-10-18)

### Bug Fixes

- Url returns 404
  ([`a7aaac6`](https://github.com/RedHatInsights/vmaas/commit/a7aaac60b730907f01077ab671ee35a1931a1fc3))


## v2.49.0 (2023-10-18)

### Features

- **reposcan**: Store timestamp of last change of given repository
  ([`d2efc4b`](https://github.com/RedHatInsights/vmaas/commit/d2efc4b222a8887e096d2aa2484f82b17e06ca47))

RHINENG-2608


## v2.48.5 (2023-08-31)

### Bug Fixes

- Sort updates also by other fields
  ([`aa12336`](https://github.com/RedHatInsights/vmaas/commit/aa123365fc64d05a1b88283d4656818513437742))

### Chores

- Skip new vulnerabilities
  ([`5d58325`](https://github.com/RedHatInsights/vmaas/commit/5d583256a21694e3870d645b189c04953f6be5bc))


## v2.48.4 (2023-08-24)

### Bug Fixes

- Consistent affected_packages in vulnerabilities response
  ([`41667fd`](https://github.com/RedHatInsights/vmaas/commit/41667fde0d86b456aa6bcc8ea3ade716695fb945))

VMAAS-1461

### Chores

- Temporary ignore vulnerabilities in pipenv
  ([`a91e7f6`](https://github.com/RedHatInsights/vmaas/commit/a91e7f6aee413f75041dd8a1f95841b43ebcb376))


## v2.48.3 (2023-08-14)

### Bug Fixes

- Sorted availableUpdates
  ([`b5c176c`](https://github.com/RedHatInsights/vmaas/commit/b5c176c27268761491926e00a8d01d6dd2456be7))

RHINENG-1536

### Chores

- Fix new flake8 error
  ([`b168881`](https://github.com/RedHatInsights/vmaas/commit/b168881bb12e292cca623aea4a33f043734c7bf3))


## v2.48.2 (2023-07-20)

### Bug Fixes

- Consistent results
  ([`c29d8a3`](https://github.com/RedHatInsights/vmaas/commit/c29d8a31104a9d6cc6ed73882a8c092076e9eb29))

https://github.com/RedHatInsights/vmaas-lib/pull/42 VMAAS-1461

### Chores

- Upgrade to python-semantic-release 8.x.x
  ([`c38a7ad`](https://github.com/RedHatInsights/vmaas/commit/c38a7ad676713a0edb078d5dc67b1cef09c28874))


## v2.48.1 (2023-07-10)

### Bug Fixes

- Update gin-gonic to fix CVE-2023-29401
  ([`d1e1c4a`](https://github.com/RedHatInsights/vmaas/commit/d1e1c4a89806b812ee90119588d2a370ff20069d))

VULN-2713

### Chores

- **vmaas-go**: Promote vmaas-lib
  ([`ce65f6a`](https://github.com/RedHatInsights/vmaas/commit/ce65f6ad6723b22511ee1180253f0eabd8452b1e))


## v2.48.0 (2023-07-10)

### Chores

- Add apiPath to bind APIs to correct paths
  ([`b33bab6`](https://github.com/RedHatInsights/vmaas/commit/b33bab60fddd67dcbb22cddd84635719e49e9edd))

VULN-2478

- Improve vmaas-lib config
  ([`6c48d2b`](https://github.com/RedHatInsights/vmaas/commit/6c48d2b4cd1a8fa0c9853d79006b88e0429cc648))

- Remove depguard linter
  ([`5c49c18`](https://github.com/RedHatInsights/vmaas/commit/5c49c184692b793b8511cfdfabab32a24cd82d40))

- Run golangci-lint only for changes in vmaas-go dir
  ([`e701693`](https://github.com/RedHatInsights/vmaas/commit/e7016932389b683c6fca034b08da2d99f74fef67))

- Update flask to fix CVE-2023-30861 and build
  ([`d6ed82d`](https://github.com/RedHatInsights/vmaas/commit/d6ed82d046f233e7e0aed3947f509dbab78d0c1b))

### Features

- Show package_name and evra in updates response
  ([`2f9ebcc`](https://github.com/RedHatInsights/vmaas/commit/2f9ebcc660eeb388ec80f1963e00ac4253a790c4))

and bump vmaas-lib VMAAS-1458


## v2.47.0 (2023-06-05)

### Features

- Remove & replace old Slack notifications
  ([`e15e077`](https://github.com/RedHatInsights/vmaas/commit/e15e07771f7525b0090a23fa343c84f2e5cc7bb0))

VMAAS-1455


## v2.46.2 (2023-05-31)

### Bug Fixes

- **vmaas-go**: Add GOMEMLIMIT to remove GOGC workaround for avoiding OOMKill
  ([`17939d2`](https://github.com/RedHatInsights/vmaas/commit/17939d2ddff0895201e68a4dd9aeb267965cce02))

### Chores

- Run golangci-lint
  ([`823e45e`](https://github.com/RedHatInsights/vmaas/commit/823e45e16fd1e5677328b56def3cc52da90c4df6))

- Update go1.19 and dependencies
  ([`7c90ac2`](https://github.com/RedHatInsights/vmaas/commit/7c90ac2b9cb0ba9fc35a1b6de9f7f2deb3c76ba2))


## v2.46.1 (2023-05-31)

### Bug Fixes

- Return 400 if processing of packages or modules fails
  ([`cce1136`](https://github.com/RedHatInsights/vmaas/commit/cce11365623eebdc0a6738f6545c68bdf17b02f3))

### Chores

- Add vmaas-go metrics to dashboard
  ([`7f6f44f`](https://github.com/RedHatInsights/vmaas/commit/7f6f44fb6e86828a567f8594028e99936046f2db))

- Change minReplicas -> replicas
  ([`012180c`](https://github.com/RedHatInsights/vmaas/commit/012180c6b806359028b3a0ad8f4d5c8a1943a8e5))

minReplicas is deprecated

- Check if podman/docker is usable
  ([`0c85c98`](https://github.com/RedHatInsights/vmaas/commit/0c85c98addbcaa88179b1d47912cf9a0a11b1fe9))

- Drop webapp_utils and refresh Pipenv lock
  ([`62b5e8b`](https://github.com/RedHatInsights/vmaas/commit/62b5e8b48da16ea02fa09185a678ef2805dd7ca2))

- None driver doesn't work as expected, use non-default profile
  ([`3016d11`](https://github.com/RedHatInsights/vmaas/commit/3016d116eef087e8c30840132805a0a3e62cbc34))

- Remove custom probes for webapp-go
  ([`a67ea50`](https://github.com/RedHatInsights/vmaas/commit/a67ea50c02ab4d62cf0853c4876364b11b134d89))

- Run webapp-go by default in environments
  ([`96cb084`](https://github.com/RedHatInsights/vmaas/commit/96cb0845385f8b089c2e3dc17bff535c59c88364))

- Switch OVAL_UNFIXED_EVAL_ENABLED default to TRUE
  ([`923a5a6`](https://github.com/RedHatInsights/vmaas/commit/923a5a6651833acffca72c7c990f8bc41ce7a589))

- Use different approach to connect from vuln-engine
  ([`426ad0a`](https://github.com/RedHatInsights/vmaas/commit/426ad0a9d9b27bad97a2bcbec5ac5eea64518496))

- Webapp-go doesn't support OVAL_UNFIXED_EVAL_ENABLED flag
  ([`8145b47`](https://github.com/RedHatInsights/vmaas/commit/8145b47c3c06b7b661c8fec3ccaab5f87b824f57))


## v2.46.0 (2023-05-16)

### Features

- Add epoch_required request option
  ([`44bf2d3`](https://github.com/RedHatInsights/vmaas/commit/44bf2d33ddeba8827a87a0c8fa17f8bcd7d8e748))

return error if pkg epoch is required and any pkg in request is missing epoch

RHINENG-390


## v2.45.2 (2023-05-15)

### Bug Fixes

- Backport changed order evaluation (unfixed, fixed) to py
  ([`7631038`](https://github.com/RedHatInsights/vmaas/commit/76310389503b44a1692c932ab36c109b0c8b58b1))

- Backport current package module detection to py
  ([`ed022a1`](https://github.com/RedHatInsights/vmaas/commit/ed022a127ea038752bfa07753512d6e9421e6ac9))

- Use standardized compare func
  ([`12fa9b2`](https://github.com/RedHatInsights/vmaas/commit/12fa9b259ec2bc2d6488ff9d603e6567b3b11e6b))

this custom py implementation is buggy sometimes

{ "package_list": ["libxml2-0:2.9.1-6.0.3.el7_9.6.x86_64"], "repository_list":
  ["rhel-7-server-rpms"] }


## v2.45.1 (2023-05-15)

### Bug Fixes

- **modules**: Package from module with disabled repo
  ([`aa79953`](https://github.com/RedHatInsights/vmaas/commit/aa79953c89441d1b6eedba9661957aacedaca2b6))


## v2.45.0 (2023-05-10)

### Features

- **oval**: Show package name, evra, cpe for unpatched cves
  ([`48f5c03`](https://github.com/RedHatInsights/vmaas/commit/48f5c03932a13d683522db3b6313b1b48360e103))

VMAAS-1454


## v2.44.0 (2023-05-09)

### Features

- **oval**: Unpatched cves take precedence
  ([`83e1d3b`](https://github.com/RedHatInsights/vmaas/commit/83e1d3bb9314d9282339eea02f8d28ab581ca916))


## v2.43.1 (2023-05-03)

### Bug Fixes

- **webapp-go**: Oval and modules fixes
  ([`1b7b69f`](https://github.com/RedHatInsights/vmaas/commit/1b7b69fe529125048e98679c6e8b1fe798fd2485))

oval: Check module stream in evaluateModuleTest (20be8ac)

oval: Remove duplicates from UnpatchedCves list (9c48307)

modules: Find updates in modular errata for package from module when module is enabled (cd99eef)


## v2.43.0 (2023-04-20)

### Chores

- Change to single quotes to fix test run on macos
  ([`bdf073c`](https://github.com/RedHatInsights/vmaas/commit/bdf073cc7d50d6aba89aa652ffe6707bb75e02a9))

- Disable tests which needs to be fixed
  ([`97b3ed4`](https://github.com/RedHatInsights/vmaas/commit/97b3ed423aebbfb4c9200bc49fa35c134a9ad5b8))

### Features

- Always use optimistic updates, also for known packages
  ([`f0d4437`](https://github.com/RedHatInsights/vmaas/commit/f0d4437e1417a660fc3b354c4edfcd2f8be4a150))

VMAAS-1394


## v2.42.4 (2023-04-03)

### Bug Fixes

- **vmaas-go**: Modules_list consistency with python
  ([`b136588`](https://github.com/RedHatInsights/vmaas/commit/b1365886e224e065a1162cca7cc08ac160346b52))


## v2.42.3 (2023-03-30)

### Bug Fixes

- **vmaas-go**: Don't gzip response from python vmaas
  ([`6322d12`](https://github.com/RedHatInsights/vmaas/commit/6322d1236f78a114ecb1777eaf2990f15ecc0cd8))


## v2.42.2 (2023-03-30)

### Bug Fixes

- **vmaas-go**: Bump to vmaas-lib with fixed locking
  ([`1f9d720`](https://github.com/RedHatInsights/vmaas/commit/1f9d7206debb181787ae05b7b36998d84013ab58))

### Chores

- Vmaas_env is now copy of ENV_NAME
  ([`59301a0`](https://github.com/RedHatInsights/vmaas/commit/59301a09faaaea7859eb5c7920304e860d8efc9d))


## v2.42.1 (2023-03-29)

### Bug Fixes

- **webapp**: Ssl context usage
  ([`cb98723`](https://github.com/RedHatInsights/vmaas/commit/cb98723577148d9b65b85407576aeb46c704f405))

### Chores

- Don't deploy webapp-go by default yet
  ([`770b072`](https://github.com/RedHatInsights/vmaas/commit/770b072acf2d1b5025e126e3d5def3e84e8d8014))

enable in each env explicitly

- **webapp**: Catch and log all other errors in timer
  ([`b7f6ea0`](https://github.com/RedHatInsights/vmaas/commit/b7f6ea0115a3d99dca5291e0d362c6f9d1085f13))

they are logged when app exits otherwise


## v2.42.0 (2023-03-29)

### Chores

- **vmaas-go**: Bump vmaas-lib to 0.4.0
  ([`fe5ae35`](https://github.com/RedHatInsights/vmaas/commit/fe5ae35221bb17c30419b9c61b1f6eae6675a3e8))

- **vmaas-go**: Re-use logging logic from patchman
  ([`d158cdd`](https://github.com/RedHatInsights/vmaas/commit/d158cdd6bb9b363a8df13f78bda73cc12dabd43d))

Co-authored-by: Michael Mraka <michael.mraka@redhat.com>

- **vmaas-go**: Set default cache refresh to 1m
  ([`0016b72`](https://github.com/RedHatInsights/vmaas/commit/0016b721c8be2cc6a34a39d6a5ede227b040e0c0))

- **vmaas-go**: Update vmaas-lib to stream dump to file
  ([`d1b3353`](https://github.com/RedHatInsights/vmaas/commit/d1b3353e67bef7ba3ca3bf42da0b47769a5585b6))

### Features

- **reposcan**: Add oval_definition_errata to cache
  ([`9a16df6`](https://github.com/RedHatInsights/vmaas/commit/9a16df619d8cf7ac4a103b3da9fba85cf4c925ef))

- **webapp**: Include errata for manually fixable cves
  ([`e811912`](https://github.com/RedHatInsights/vmaas/commit/e8119125b58ed36cec2b9a3423c80eb01534100e))

- **webapp**: Support many erratas for manually fixable cve
  ([`54b7099`](https://github.com/RedHatInsights/vmaas/commit/54b709947f930cfaa3447df37107f9dfe4927479))


## v2.41.1 (2023-03-28)

### Bug Fixes

- Docker-compose build
  ([`25e44da`](https://github.com/RedHatInsights/vmaas/commit/25e44da7856cb52960dc492c0a14ffcbb1482ef2))

- Handle exception when sending slack notification
  ([`7379d2a`](https://github.com/RedHatInsights/vmaas/commit/7379d2ae7a59dbf69373e0c6b3ffe9bb8f986201))

### Chores

- Update clowdapp params to stage defaults
  ([`a919cb1`](https://github.com/RedHatInsights/vmaas/commit/a919cb1a71d0c1410a10d2f3db7a5880e4e13f60))


## v2.41.0 (2023-03-27)

### Chores

- Add instructions how to copy database from openshift
  ([`b13ea25`](https://github.com/RedHatInsights/vmaas/commit/b13ea255dda3ecfcff8b3e87541575629eb06955))

- Remove generic docker setup and obsolete openshift steps
  ([`a9770ff`](https://github.com/RedHatInsights/vmaas/commit/a9770ff485f79d57041803b4dfe751d2c4a723fb))

- Remove websocket occurrences
  ([`742c3da`](https://github.com/RedHatInsights/vmaas/commit/742c3da8b260dd1e2c0b88b168bafdc53f702589))

- Use nginx to serve dump files
  ([`9f79857`](https://github.com/RedHatInsights/vmaas/commit/9f798575e4b6c1b213169f30e60cb7ed5fffe968))

reposcan webserver is single-threaded and serving large files is causing timeouts

- **vmaas-go**: Remove unused websocket url
  ([`b60486e`](https://github.com/RedHatInsights/vmaas/commit/b60486e4668ae36e824f4ef9e195c78ac717c249))

### Features

- **webapp**: Use timer instead of websocket to refresh data
  ([`4e14fa7`](https://github.com/RedHatInsights/vmaas/commit/4e14fa7db8511b4a09238ea6ca2b487f9dcebc2a))


## v2.40.0 (2023-03-14)

### Bug Fixes

- **fedramp**: Set tls ca for dump download
  ([`7d27e62`](https://github.com/RedHatInsights/vmaas/commit/7d27e620206c54e5b4f10cce6ffc0f84effe1f42))

### Chores

- Build repolist to the image
  ([`739c7a7`](https://github.com/RedHatInsights/vmaas/commit/739c7a7f69b5c08a08f8921b37a8c8bf3d954a61))

- Downgrade do ubi8 but with Python 3.9
  ([`78fcfb7`](https://github.com/RedHatInsights/vmaas/commit/78fcfb759b786482aa4933795f41282796b775cb))

- Pylint fixes
  ([`d5b3c61`](https://github.com/RedHatInsights/vmaas/commit/d5b3c61692cca54e023693733c17ae788de704aa))

- Replace rsync with http
  ([`350bd9c`](https://github.com/RedHatInsights/vmaas/commit/350bd9ccef4efc19f8aa65b1167dd3558739b23e))

- Temporarily ignore vulnerability 53048
  ([`534c002`](https://github.com/RedHatInsights/vmaas/commit/534c0026074dc782074da20a9ecec9db71fb5eec))

- Update app-common libs
  ([`eefc8e1`](https://github.com/RedHatInsights/vmaas/commit/eefc8e105f0b1c191ee68493ea8b265fe70e2ad9))

- **reposcan**: Deprecate pkgtree generation
  ([`c2d0c56`](https://github.com/RedHatInsights/vmaas/commit/c2d0c56c08ca37d593b153b156f182f385e18fbd))

- **reposcan**: Use repolist from static path in image in FedRAMP deployment
  ([`c76d96a`](https://github.com/RedHatInsights/vmaas/commit/c76d96a2ccb8399e5d08f913564d84206c6b289c))

### Features

- **fedramp**: Use tls for outgoing connections and simplify config
  ([`e3e9e71`](https://github.com/RedHatInsights/vmaas/commit/e3e9e719bb97b4f904e45af14d6d8b5b5a7281fb))

RHINENG-95

TODO: investigate how to use TLS with rsync

### Testing

- Fix tests by specifying db password
  ([`c489e6f`](https://github.com/RedHatInsights/vmaas/commit/c489e6faaef23e13e1d51344d53515b005bef5ab))


## v2.39.3 (2023-02-17)

### Bug Fixes

- **vmaas-go**: Incorrect json field for third_party updates
  ([`eb39dba`](https://github.com/RedHatInsights/vmaas/commit/eb39dba5f82f97135085b4ca11af637f37e7daef))

SPM-1869

- **vmaas-go**: Panic during refresh
  ([`5d2f900`](https://github.com/RedHatInsights/vmaas/commit/5d2f9001de52e89af17e698c14c0ec8a7dc53312))

VMAAS-1446

- **vmaas-go**: Return errata: [] instead of null
  ([`23908a8`](https://github.com/RedHatInsights/vmaas/commit/23908a8f96282377c3751ae8ff8acb34b0875572))

VMAAS-1447

### Chores

- Don't run iqe tests against vmaas-go
  ([`b798351`](https://github.com/RedHatInsights/vmaas/commit/b7983519db8158c4ce9373eb6435e4164cb45b00))

VMAAS-1439


## v2.39.2 (2023-01-23)

### Bug Fixes

- Inconsistent response for invalid packages
  ([`cdf3f48`](https://github.com/RedHatInsights/vmaas/commit/cdf3f488174c9a10ae65e1cc6b0c18fdc33475a8))

update for single invalid package (erp-handler-0:-.i386) returns: "update_list": {
  "erp-handler-0:-.i386": {} }

but when there are 2 invalid packages in the request, ("package_list": ["cel-handler-0:-.i386,
  erp-handler-0:-.i386"]) then it returns 400. the expected response is: "update_list": {
  "cel-handler-0:-.i386": {}, "erp-handler-0:-.i386": {} }


## v2.39.1 (2023-01-20)

### Bug Fixes

- Allow null repository_list
  ([`0dc8546`](https://github.com/RedHatInsights/vmaas/commit/0dc8546191054bec26832c2338829226789406f4))

VULN-2519


## v2.39.0 (2023-01-13)

### Features

- **vmaas-go**: Use goroutines
  ([`6859dca`](https://github.com/RedHatInsights/vmaas/commit/6859dca4da5863c528d68494cdd07de3e4e8f639))

VMAAS-1436


## v2.38.2 (2023-01-10)

### Bug Fixes

- Watchtower params
  ([`02ccf10`](https://github.com/RedHatInsights/vmaas/commit/02ccf1026592dfc42b1a0b763fcfb9667d0e04cb))


## v2.38.1 (2023-01-09)

### Bug Fixes

- **vmaas-go**: Incorrect cve-errata mapping
  ([`56094cf`](https://github.com/RedHatInsights/vmaas/commit/56094cffee0ffaff4b4e7218af51a03b69f9f2d6))


## v2.38.0 (2023-01-09)

### Chores

- Test failures and minor changes recommended by pylint
  ([`6c9e552`](https://github.com/RedHatInsights/vmaas/commit/6c9e5522f4408a62991206b03e42f6e3db83ab6a))

- Update pylintrc
  ([`2b267a9`](https://github.com/RedHatInsights/vmaas/commit/2b267a90d2bbf996af75a8a6e929516e6e1c588b))

- **pylint**: Add slack notification post timeout
  ([`064b858`](https://github.com/RedHatInsights/vmaas/commit/064b858061544a5052799b9b3b4e3a33a78c5ea0))

### Features

- Use ubi9, python3.9, go1.18
  ([`c3e3b60`](https://github.com/RedHatInsights/vmaas/commit/c3e3b602fc8c6731bed14550cde967c5287cb495))

VMAAS-1443


## v2.37.11 (2023-01-05)

### Bug Fixes

- **vmaas-go**: Cache reload, adjust GOGC
  ([`3ab6317`](https://github.com/RedHatInsights/vmaas/commit/3ab6317ef2c2f5547729f78553adf897fa9d46f3))

### Chores

- **pipenv**: Ignore new vulns for now
  ([`663ea90`](https://github.com/RedHatInsights/vmaas/commit/663ea90fa87866a0804b24c8d55cd9fbd6b1570a))


## v2.37.10 (2022-12-19)

### Bug Fixes

- **vmaas-go**: Update vmaas-lib and set GC
  ([`6572ef5`](https://github.com/RedHatInsights/vmaas/commit/6572ef513ae21f909cdbc0109f54c57d85b2306c))

### Chores

- Replace deprecated set-output command
  ([`eae365c`](https://github.com/RedHatInsights/vmaas/commit/eae365cb3d2cbe78d6f049f0722dd27b9ce0fe89))

VMAAS-1440


## v2.37.9 (2022-12-15)

### Bug Fixes

- **vmaas-go**: Optimizations
  ([`8d2639c`](https://github.com/RedHatInsights/vmaas/commit/8d2639cda988217648216d6aff5421a92fdd1131))


## v2.37.8 (2022-12-12)

### Bug Fixes

- **vmaas-go**: Updates when releasever in repo is empty
  ([`80c86c0`](https://github.com/RedHatInsights/vmaas/commit/80c86c0fa5e41a4b8a3e6333a2b7328812f5818d))


## v2.37.7 (2022-12-08)

### Bug Fixes

- **vmaas-go**: Bump vmaas-lib version to fix arch compatibility
  ([`ecbd93a`](https://github.com/RedHatInsights/vmaas/commit/ecbd93a022662f0d79e1bf4edfe0cb2868cb231f))


## v2.37.6 (2022-12-08)

### Bug Fixes

- **vmaas-go**: Add metrics
  ([`daf67c0`](https://github.com/RedHatInsights/vmaas/commit/daf67c0c6731b7bcb17f2d3952b50faa9776b8df))

VMAAS-1437

### Chores

- Update vmaas-go deps
  ([`01c0803`](https://github.com/RedHatInsights/vmaas/commit/01c0803d01d1bc05726f3703ba2556a7af2742a7))

### Testing

- **vmaas-go**: Probe test
  ([`8c73ffa`](https://github.com/RedHatInsights/vmaas/commit/8c73ffae7c2bed9aaeee1a03831468a2fa46bbe8))


## v2.37.5 (2022-12-07)

### Bug Fixes

- **vmaas-go**: Recover from panic and respond 500
  ([`09be0db`](https://github.com/RedHatInsights/vmaas/commit/09be0db507bf35ad9a32241beb9ae47e820858eb))

### Chores

- **vmaas-go**: Update vmaas-lib
  ([`16901cf`](https://github.com/RedHatInsights/vmaas/commit/16901cfa10dcda729be13dde5ed0709dae0b0ff0))


## v2.37.4 (2022-11-25)

### Bug Fixes

- **vmaas-go**: Don't proxy request when error is present
  ([`6c86060`](https://github.com/RedHatInsights/vmaas/commit/6c86060465d95830b866e405bcdb5b5aa719a93e))


## v2.37.3 (2022-11-25)

### Bug Fixes

- **vmaas-go**: Return 503 during cache reload
  ([`6913cc9`](https://github.com/RedHatInsights/vmaas/commit/6913cc9b7a734db169c063c3d9bbe68d0a44d412))

VMAAS-1438


## v2.37.2 (2022-11-24)

### Bug Fixes

- Define cpu/memory limit/requests separately
  ([`22a96d9`](https://github.com/RedHatInsights/vmaas/commit/22a96d96015a1d3a0d7ece3d317a3a333a35852d))


## v2.37.1 (2022-11-23)

### Bug Fixes

- **probes**: Define custom probes
  ([`7a5c438`](https://github.com/RedHatInsights/vmaas/commit/7a5c4384f4f5e811cfb263817d9ec328869a4179))

### Chores

- Bump python version in tests
  ([`47cd2ef`](https://github.com/RedHatInsights/vmaas/commit/47cd2ef9978d12e66b8882fa32d18a3091a8dbe7))

- **vmaas-go**: Don't block on cache load
  ([`05db4bc`](https://github.com/RedHatInsights/vmaas/commit/05db4bce20a0d626ed8d6b8d8137870c995ecfcb))


## v2.37.0 (2022-11-22)

### Bug Fixes

- **updates**: Repository_paths used alone
  ([`2cac2b4`](https://github.com/RedHatInsights/vmaas/commit/2cac2b4a28f00cba3f9d01f11e568e3327c4636a))

Allow to use `repository_paths` parameter with updates API without specifying `repository_list`.
  Otherwise it would use all avilable repostiories if `repository_list` is not provided.

VULN-2443

### Features

- **cache**: Repository id by path
  ([`47bc078`](https://github.com/RedHatInsights/vmaas/commit/47bc07893f90d352dd8cb2be2f974eba123ba70e))

Cache repository ids by path from parsed from their URL. This is to enable RHUI machines support,
  which use different repository labels.

VULN-2443

- **updates**: Look up updates by repository paths
  ([`5ce94f0`](https://github.com/RedHatInsights/vmaas/commit/5ce94f082c29d9bb64025d65be2f39a12622c7b2))

Provide an option to look up updates by providing repository paths (as an addition to repository
  labels).

This should support tracking updates and vulnerabilities within RHUI enabled machines, as it would
  not be dependent on repository labels.

VULN-2443

- **vulnerabilities**: Vulns by repository_paths
  ([`985ad04`](https://github.com/RedHatInsights/vmaas/commit/985ad04c243e9569b46327813f567cdb303dd087))

Provide an option to look up vulnerablities by providing repository paths (as an addition to
  repository labels).

This should support tracking updates and vulnerabilities within RHUI enabled machines, as it would
  not be dependent on repository labels.

VULN-2443

### Refactoring

- **tests**: Split cache tests and create fixtures
  ([`2032c21`](https://github.com/RedHatInsights/vmaas/commit/2032c2135b4a86f3bb1eb2e35286ce2585f2a539))

VULN-2443

- **updates**: All repositories as list
  ([`cff6d71`](https://github.com/RedHatInsights/vmaas/commit/cff6d711c1bfcefe2437389bfb700c32efffc786))

VULN-2443

### Testing

- **modularity**: Robust assertions
  ([`fece842`](https://github.com/RedHatInsights/vmaas/commit/fece8426e9e19e587597780c10fff2a5fc0c13ca))

Make some assertion robust to expect updates for the same package from more than one erratum.

VULN-2443


## v2.36.0 (2022-11-22)

### Chores

- **vmaas-go**: Run PR check
  ([`858cdf6`](https://github.com/RedHatInsights/vmaas/commit/858cdf6c067feca35650ac32aefedf6519685df6))

VMAAS-1431

### Features

- **webapp-go**: App handling updates and vulnerabilities
  ([`c7436c1`](https://github.com/RedHatInsights/vmaas/commit/c7436c1b2e54b5c204116a711c611e05ab5f3fb2))

VMAAS-1431

- **webapp-go**: Base and utils based on redhatinsights/patchman-engine
  ([`133b098`](https://github.com/RedHatInsights/vmaas/commit/133b098c1f124ff0d5d812a6772fe397259ad736))

VMAAS-1431

- **webapp-go**: Build and deployment
  ([`5ab7743`](https://github.com/RedHatInsights/vmaas/commit/5ab7743bd8a3d289d0d4e14a5b9e5a1adf62c137))

VMAAS-1431

- **webapp-go**: Local config
  ([`b01edf3`](https://github.com/RedHatInsights/vmaas/commit/b01edf39917cc917771c54be8299311c7f11639b))

VMAAS-1431


## v2.35.4 (2022-11-14)

### Bug Fixes

- **tests**: Skip unrelated pipenv check
  ([`bfe0a7b`](https://github.com/RedHatInsights/vmaas/commit/bfe0a7ba750db0ba4e323e96fa362530e7dbee0b))

VULN-2443

- **tests**: Test env vars unqoted
  ([`4800058`](https://github.com/RedHatInsights/vmaas/commit/4800058fcbdfdae4d15049602d10905fcf9a62d4))

Quotes in Linux when setting env vars are taken as literals. This also fixes use with podman-compose
  and direct runs within the test container.

VULN-2443

### Chores

- Remove unused file
  ([`7be05c8`](https://github.com/RedHatInsights/vmaas/commit/7be05c8031fe40a2d88376251f2d6d9105918a28))


## v2.35.3 (2022-10-07)

### Bug Fixes

- **reposcan**: Collect prometheus metrics from child processes
  ([`4c16942`](https://github.com/RedHatInsights/vmaas/commit/4c16942abe5817c5a479d46f14d0ec7805d15afd))

VMAAS-992


## v2.35.2 (2022-07-19)

### Bug Fixes

- Run flake8 in GH actions and fix flake8 issues
  ([`ca6d8c1`](https://github.com/RedHatInsights/vmaas/commit/ca6d8c1782a2122a028f247078ab35257c9ab7c9))

VMAAS-1425

### Chores

- Disable pylint lower than 2 . 13 . 0 check
  ([`5d8344e`](https://github.com/RedHatInsights/vmaas/commit/5d8344e31f633bb8606a94dd0238617bfe17bbd8))

- Get repos from RedHatInsights repo
  ([`d1704b2`](https://github.com/RedHatInsights/vmaas/commit/d1704b2533f963a3e2bacdd03725e69301fd0c13))

- Remove dump files in old format
  ([`f6c41dd`](https://github.com/RedHatInsights/vmaas/commit/f6c41dd6eba06040bdc8592011649b951099d8b3))

- Remove dump files in old format even in case of error
  ([`eded3de`](https://github.com/RedHatInsights/vmaas/commit/eded3de4ffe183d2e161a515554d4e8e6b185577))

- Revert remove dump files in old format changes
  ([`9924b21`](https://github.com/RedHatInsights/vmaas/commit/9924b21f230993b06918a89fff0551b98a9d819d))

the problem was resolved

This reverts commit 302c11c5c70d10c5343b3803064e68cc151e6d0b. This reverts commit
  d3e19f1b3a6054ca9e58ad27217e614eda7adec8.

- Rewrite unittest tests to pytest
  ([`868ab3e`](https://github.com/RedHatInsights/vmaas/commit/868ab3e2b344d76765c2869b5fe25f77390c3b11))

VMAAS-155


## v2.35.1 (2022-05-30)

### Bug Fixes

- Rename epel repo to epel-8
  ([`7b13602`](https://github.com/RedHatInsights/vmaas/commit/7b1360265a1eeba3e35c419b40318d48546138e7))

### Chores

- Add PR template
  ([`6547a6b`](https://github.com/RedHatInsights/vmaas/commit/6547a6b5bd39e699aa3623b078b8f8f5c7dea76c))

- Add repo name prefixes to be stripped
  ([`6883337`](https://github.com/RedHatInsights/vmaas/commit/688333781f522d50c81c3edbd43c7cdd08220044))

- Rebasing on top of base branch is now natively available from github UI
  ([`718b631`](https://github.com/RedHatInsights/vmaas/commit/718b6315513d5da4b53d3015ce90c9938e1b0054))


## v2.35.0 (2022-03-07)

### Features

- **webapp**: Strip prefixes from repository names
  ([`bcd2572`](https://github.com/RedHatInsights/vmaas/commit/bcd2572de2b192a1b98a8e5b4de91ea7d74b2c87))


## v2.34.6 (2022-03-02)

### Bug Fixes

- **reposcan**: Fix lint in test_patchlist.py
  ([`b71de25`](https://github.com/RedHatInsights/vmaas/commit/b71de25e43286e5d39270b70af6844a4d2e42160))


## v2.34.5 (2022-03-01)

### Bug Fixes

- **reposcan**: Handle all other sync exceptions to not skip syncing valid repos
  ([`9d355da`](https://github.com/RedHatInsights/vmaas/commit/9d355da4f13585c3d9a50ff1220a0e252011cf83))

### Chores

- Special compose for podman is no more needed
  ([`24757a5`](https://github.com/RedHatInsights/vmaas/commit/24757a5138c89849ac98630fc2096f0887730b6a))

- Vmaas_databasefix is no longer needed
  ([`2686b0f`](https://github.com/RedHatInsights/vmaas/commit/2686b0f2babf3e24659c1f5a37058d1eda84dc3c))


## v2.34.4 (2022-02-22)

### Bug Fixes

- **local-deployment**: Official PostgreSQL container has different mount path
  ([`9fcc693`](https://github.com/RedHatInsights/vmaas/commit/9fcc69332f5bd91189e2918eb86fc1dc534bd331))

### Chores

- **repolist**: Add rhel 8.1 eus repo
  ([`af34b38`](https://github.com/RedHatInsights/vmaas/commit/af34b38a3360601d355dd10c243e4700899f2bb4))


## v2.34.3 (2022-02-14)

### Bug Fixes

- **reposcan**: Eus repos are mapped to CPEs of incorrect EUS version
  ([`f9fc5da`](https://github.com/RedHatInsights/vmaas/commit/f9fc5da8b88011bf80637c30131e66598ac2a40e))

VMAAS-1414

### Chores

- Add missing slack webhook
  ([`4a58391`](https://github.com/RedHatInsights/vmaas/commit/4a58391d99460349656892fff8ab4f179f9398d9))

- Add missing VMAAS_ENV
  ([`6e47c1b`](https://github.com/RedHatInsights/vmaas/commit/6e47c1b3598ddbd7bea7c1adbbbd7e79cda7b881))

- Process repositories in deterministic order
  ([`6c9b331`](https://github.com/RedHatInsights/vmaas/commit/6c9b3314f9c15c5756f919bdd5dcc25e41c0648b))


## v2.34.2 (2022-02-07)

### Bug Fixes

- **reposcan**: Don't delete whole CS when want to delete only repo with null basearch and
  releasever
  ([`862c2cb`](https://github.com/RedHatInsights/vmaas/commit/862c2cb67a7a2fd74eed1f86a60d40ff0bb8681d))

- **webapp**: In errata_associated CVE list include also CVEs found only in OVAL files (missing in
  repodata due to error)
  ([`4b0157e`](https://github.com/RedHatInsights/vmaas/commit/4b0157ef9994931d16549659efae80339c8c02cd))

VULN-1412

### Chores

- Pylint
  ([`bfec00d`](https://github.com/RedHatInsights/vmaas/commit/bfec00d2d92115563d8809eed6094b799b7eef74))

- Used CentOS 8 Stream in Dockerfile (Centos 8 EOL)
  ([`1cccc89`](https://github.com/RedHatInsights/vmaas/commit/1cccc89ee7d8ab278bfc793dce1dead57dfc73d0))


## v2.34.1 (2022-02-02)

### Bug Fixes

- **reposcan**: Allow redirects
  ([`dc433c8`](https://github.com/RedHatInsights/vmaas/commit/dc433c861551b34aec2a2713118fd12c2fefebc7))

### Chores

- Update pipenv
  ([`23424f7`](https://github.com/RedHatInsights/vmaas/commit/23424f7177b79b4beafbd053984851accb59312c))

- **gh-actions**: Delete integration-tests-local
  ([`545b007`](https://github.com/RedHatInsights/vmaas/commit/545b0070b9792681ab566d2dbe8fb1fdfcd13747))

- **pr_check**: Always create artifacts dir
  ([`eb8a0a6`](https://github.com/RedHatInsights/vmaas/commit/eb8a0a69089ba5ae662891b5eda9213d3d0e9f9d))


## v2.34.0 (2022-01-25)

### Chores

- Prometheus metric for count of repos requiring cleanup
  ([`0b0ec66`](https://github.com/RedHatInsights/vmaas/commit/0b0ec66b316a7ce1961fc0bcc67dd00519aeca90))

- Remove legacy service objects
  ([`846fc10`](https://github.com/RedHatInsights/vmaas/commit/846fc109149726cfa81c4633267ec52b62701cc8))

VMAAS-1404

### Features

- **reposcan**: Delete all repos removed from list
  ([`e9ec3a8`](https://github.com/RedHatInsights/vmaas/commit/e9ec3a81bb08595a8d3d17168c0b1b26ca5aacfc))

VMAAS-1409


## v2.33.1 (2022-01-21)

### Bug Fixes

- **webapp**: Remove null probes in clowaddp.yaml
  ([`5e38b8d`](https://github.com/RedHatInsights/vmaas/commit/5e38b8dd703fc453285c0d7b36dcc9ff2ee0da19))

- because of clowder upgrade

### Chores

- **tests**: Sync eus repos for integration tests
  ([`45595a7`](https://github.com/RedHatInsights/vmaas/commit/45595a7318c08d505ec5355e736c97e7b7effa99))

VMAAS-1408


## v2.33.0 (2022-01-18)

### Chores

- Disable autostart of grafana and prometheus
  ([`5fd3f37`](https://github.com/RedHatInsights/vmaas/commit/5fd3f3780a591cb6f608b9c1d3d6b9d0647600c3))

- Removed dev database files
  ([`abead8b`](https://github.com/RedHatInsights/vmaas/commit/abead8b271364a946c5a35c7c9ae309333eedfae))

- replaced with official postgres container - VMAAS-1405

- Use vmaas.reposcan.database.upgrade in tests
  ([`5a9e483`](https://github.com/RedHatInsights/vmaas/commit/5a9e4832ff2278ebd9c639ef64aaea4b060638b9))

- include wait_for_services.py into "common" sub-package - VMAAS-1405

- Used offic. docker image for testing db
  ([`abf6e66`](https://github.com/RedHatInsights/vmaas/commit/abf6e663e53cada4be482992031e4c752fcecc92))

- VMAAS-1405

### Features

- **reposcan**: Link CPEs with specific repos, not only content sets
  ([`428bfad`](https://github.com/RedHatInsights/vmaas/commit/428bfad8e974ae0b0107d7fd557fb842f9b333aa))

VMAAS-1402

- **webapp**: Use CPE-repository mapping if available
  ([`9e06241`](https://github.com/RedHatInsights/vmaas/commit/9e06241f5b3ac8fb28672154739a7a3afc71380d))

VMAAS-1402


## v2.32.11 (2022-01-10)

### Bug Fixes

- **reposcan**: Fix vmaas_reader password setting
  ([`3ac9888`](https://github.com/RedHatInsights/vmaas/commit/3ac98880b8b97cb2d933f78918c370ee37095abf))

### Chores

- Added common.paths file to define file paths constants
  ([`ef444cd`](https://github.com/RedHatInsights/vmaas/commit/ef444cd94478aa1b7d21076acf39dfd8e31e8114))

- VMAAS-1403

- Added grafana config script "scripts/grafana-json-to-yaml.sh"
  ([`1aa335a`](https://github.com/RedHatInsights/vmaas/commit/1aa335a3064bbba82211d92854a0b160041c9779))

- Improve logging in wait_for_services
  ([`98c5c4e`](https://github.com/RedHatInsights/vmaas/commit/98c5c4e6362bee1db8b74281f9df95d947690084))

- Keep database folder path in container
  ([`9b015d2`](https://github.com/RedHatInsights/vmaas/commit/9b015d2bf66260347a152f1543047f37490e6d51))

- VMAAS-1403

- Made "test_integration.test_phase_2" independent and idempotent
  ([`fdf515c`](https://github.com/RedHatInsights/vmaas/commit/fdf515cc54bac433f1c98c1d60f2d6eb1a1c7ad9))

- VMAAS-1403

- Refactored testing sql scripts (vmaas/reposcan/test_data/database)
  ([`9c19411`](https://github.com/RedHatInsights/vmaas/commit/9c19411c8a39681a8226b5b245ccfcdff151a154))

- VMAAS-1403

- Remove DB_UPGRADE_SCRIPTS_DIR var from clowdapp.yaml
  ([`f2e7533`](https://github.com/RedHatInsights/vmaas/commit/f2e7533553ff932713a152bfd5cd42d2790df61e))

- VMAAS-1403

- Simplified upgrading test (test_upgrades.py)
  ([`1a144b9`](https://github.com/RedHatInsights/vmaas/commit/1a144b9e9c1779550a5dcddaf55ae5f39b5b080c))

- VMAAS-1403

- Unified conftest.py, removed redundant files
  ([`1bc41a1`](https://github.com/RedHatInsights/vmaas/commit/1bc41a15ee272ec171fca984b5fcc7844d167174))

- VMAAS-1403

- Updated "Dockerfile" to be used also for tests
  ([`c7c758c`](https://github.com/RedHatInsights/vmaas/commit/c7c758c346f4b69ba1479df0d86b23994e4c04d8))

- VMAAS-1403 - removed Dockerfile.test

- Updated docker-compose.test.yml to use Dockerfile, added db container
  ([`7854a14`](https://github.com/RedHatInsights/vmaas/commit/7854a1478209499cd224f7f5a53d5a9617e3e3b4))

- VMAAS-1403 - create db superuser "vmaas_admin" (database/init_schema.sh) - added testing conf env
  file (test.env)

- Updated grafana board
  ([`e061b87`](https://github.com/RedHatInsights/vmaas/commit/e061b8747a36d17d7b314658868e333bce3ef718))

- added important signals (traffic rate, latency - overal and per handler) - added resources usage
  charts - added additional charts (containers restarts, RDS usage) - updated out-of-date queries

- Updated pylintrc (added no-member) due to rpm.labelCompare issue
  ([`ceffc03`](https://github.com/RedHatInsights/vmaas/commit/ceffc033f8c6759765d931f5259278fe7378347e))

- VMAAS-1403

- Updated reposcan tests (changed db connection)
  ([`7533acb`](https://github.com/RedHatInsights/vmaas/commit/7533acb12d088412f698c6aa3586b76e0ff233c1))

- VMAAS-1403

- Use podman to build image from master
  ([`77fcb6b`](https://github.com/RedHatInsights/vmaas/commit/77fcb6b56bb322cc4e113978193d684abbc2455f))

- Use postgresql pkg from RHEL/CentOS
  ([`d5c7e59`](https://github.com/RedHatInsights/vmaas/commit/d5c7e59006469be3102d8c2d54cf6b0cbce789cd))

disable unneeded arm64 workarounds

add microdnf opts to not install unneeded packages


## v2.32.10 (2021-12-08)

### Chores

- **webapp**: Log requests
  ([`a9b1c7e`](https://github.com/RedHatInsights/vmaas/commit/a9b1c7e65307433381fc02015d945c62e3a9506a))

VMAAS-1395

### Performance Improvements

- **webapp**: Don't evaluate unfixed CVEs by default now
  ([`3bec6c8`](https://github.com/RedHatInsights/vmaas/commit/3bec6c8c936b41592c34751a61acb617399f4582))


## v2.32.9 (2021-12-07)

### Bug Fixes

- **webapp**: Allow CORS pre-flight check for /cves API
  ([`3a7c489`](https://github.com/RedHatInsights/vmaas/commit/3a7c489f5e8f72883522e1237d94611f7917bd1c))

VMAAS-1401

### Chores

- Process requirements priority labels
  ([`530ae51`](https://github.com/RedHatInsights/vmaas/commit/530ae51f12e5fe7e0ea3b09bd4da7ccbd66a3c4e))

- Renamed env var
  ([`01b0531`](https://github.com/RedHatInsights/vmaas/commit/01b0531469b126508bb54570c44b0042fc378087))

- Requirements are comma,delimited,strings
  ([`f67cd71`](https://github.com/RedHatInsights/vmaas/commit/f67cd7116a9f3128f67e6880230902b0a0469fe9))

- **reposcan**: Add more counters in oval sync
  ([`a80071b`](https://github.com/RedHatInsights/vmaas/commit/a80071b2bc2eb2126159d25d75054f55fc59657e))

VMAAS-1330


## v2.32.8 (2021-11-25)

### Bug Fixes

- **websocket**: Do not advertise None vmaas cache version
  ([`a971fe0`](https://github.com/RedHatInsights/vmaas/commit/a971fe0559c1b55b0a531cbcc29d3c0a6d044cd4))

VULN-2022


## v2.32.7 (2021-11-24)

### Bug Fixes

- **webapp**: Workaround with appProtocol tcp (clowder hardcodes http) - for istio
  ([`c5341d7`](https://github.com/RedHatInsights/vmaas/commit/c5341d7cbf3e65cac4abe21bfebd37ebeec61ffe))


## v2.32.6 (2021-11-19)

### Bug Fixes

- **reposcan**: Add template strings to properly update
  ([`60bf563`](https://github.com/RedHatInsights/vmaas/commit/60bf563b93379c9d54566121b05f427c6a2058e0))

VMAAS-1397

- **reposcan**: Fetch actual data from db progressively
  ([`bbaf703`](https://github.com/RedHatInsights/vmaas/commit/bbaf7039ce048cd2b2c4aa13412ca4140c9a38c8))

if cache is loaded on start it's invalid after cascade delete

VMAAS-1397

- **reposcan**: Use cascade delete to properly delete
  ([`74b1c78`](https://github.com/RedHatInsights/vmaas/commit/74b1c784c24cb328cade9b7c260d429e3f273ccd))

it's easiest solution to make deletions working

also remove old items from cache

VMAAS-1397

### Chores

- Bump version of development grafana
  ([`b2f750c`](https://github.com/RedHatInsights/vmaas/commit/b2f750c3083617be64d310cbdc2c48a9e9b3f2f4))

- Temporarily disable probes for webapp
  ([`5bbeac0`](https://github.com/RedHatInsights/vmaas/commit/5bbeac07773c56f005fb0be63948c13df07d64b7))

until VMAAS-1399 is resolved

- **grafana**: Fix container names
  ([`38cbfdc`](https://github.com/RedHatInsights/vmaas/commit/38cbfdc445dc2860ddfa8d108d5bedef49febb91))

- **grafana**: Fix increase iteration to re-deploy
  ([`456c21b`](https://github.com/RedHatInsights/vmaas/commit/456c21b1e0e01ebba2f11f0d196e73748ee15bdf))


## v2.32.5 (2021-11-15)

### Bug Fixes

- **reposcan**: Do not store 'None' string if last-modified header is not available
  ([`55e908a`](https://github.com/RedHatInsights/vmaas/commit/55e908a44734848c67f03d8e1c39f16c675027b8))

VMAAS-1396

### Chores

- Keep pr_check namespace with label
  ([`760e4c4`](https://github.com/RedHatInsights/vmaas/commit/760e4c4cd5d46053417ecd2e441f4966e12411f1))

- Workaround for broken pipenv
  ([`eaaa94c`](https://github.com/RedHatInsights/vmaas/commit/eaaa94cf27e766749fb3e35572c84148aee084f2))


## v2.32.4 (2021-11-12)

### Bug Fixes

- **webapp**: Use common function for parsing evr
  ([`0724a04`](https://github.com/RedHatInsights/vmaas/commit/0724a04a8cb97cedef1ddeee26430816c43adbeb))

VMAAS-1398

### Chores

- Add metrics ports for clowder
  ([`ecb8005`](https://github.com/RedHatInsights/vmaas/commit/ecb800505d0290a7e8a37c7eda4755cb76323a21))

VULN-1387

- Fix github labels in pr_check
  ([`443315a`](https://github.com/RedHatInsights/vmaas/commit/443315a41904b9666216f5a3eca6b34a077a570a))

- Fix prometheus name
  ([`9548422`](https://github.com/RedHatInsights/vmaas/commit/954842210e2b00cdc211951371545ba6a48c2848))

- Vmaas-1353 modify /packages to retun package name always
  ([`a1fe7c7`](https://github.com/RedHatInsights/vmaas/commit/a1fe7c7eb883de4a3dc0999785dd3900b7e7b114))


## v2.32.3 (2021-11-08)

### Bug Fixes

- **webapp**: Aiohttp 3.8.0 - don't create new event loop, fix websocket connection
  ([`2fb0494`](https://github.com/RedHatInsights/vmaas/commit/2fb0494d568fd4c17eb6be3995fee86b306eb3f9))

### Chores

- Update deps to fix vulnerabilities
  ([`3018df8`](https://github.com/RedHatInsights/vmaas/commit/3018df8cc0c5230005189c45a35110a06686be88))


## v2.32.2 (2021-11-08)

### Bug Fixes

- **webapp**: Rebuild index array on cache reload
  ([`9062a6e`](https://github.com/RedHatInsights/vmaas/commit/9062a6e033026e227e2bc075ce99d2d2d5ddf88b))

- VMAAS-1391


## v2.32.1 (2021-11-08)

### Bug Fixes

- **webapp**: Remove empty release versions from list
  ([`77d7267`](https://github.com/RedHatInsights/vmaas/commit/77d72670271c71ddeaf3414c2b47eea7d430acfb))

### Chores

- Fix locking script on aarch64 (/tmp unresolvable symlink and need to build psycopg2-binary)
  ([`885ca30`](https://github.com/RedHatInsights/vmaas/commit/885ca30088c6735d3cde6b5cc3fe1b9f1903d982))

- Increase timeout and delay in probes for webapp
  ([`27f35aa`](https://github.com/RedHatInsights/vmaas/commit/27f35aae537656bd511f7c15c48d4d99f9177224))

- Set cvemap url in clowdapp.yaml
  ([`708f5ae`](https://github.com/RedHatInsights/vmaas/commit/708f5ae6ce82beb625b38996d2404f8d6f3f9c3a))

- Temporarily disable probes for webapp
  ([`5eff3ba`](https://github.com/RedHatInsights/vmaas/commit/5eff3baaad66510911f0f6d34567babd165f1073))

- Use MEMORY_LIMIT also for webapp requests
  ([`2f6392e`](https://github.com/RedHatInsights/vmaas/commit/2f6392e06148b9bc7895514fe9ae44e790321f02))


## v2.32.0 (2021-11-02)

### Bug Fixes

- Upgrade db, use utc default timezon for "modified" pkg attribute
  ([`0c96b78`](https://github.com/RedHatInsights/vmaas/commit/0c96b7870b677dd63b3fe3030a47f8c4745867c7))

- VMAAS-1391

### Chores

- Add common.algorithms tests
  ([`e6c60dc`](https://github.com/RedHatInsights/vmaas/commit/e6c60dc4222414d4876a6fbef7a6866b88dd3a4b))

- VMAAS-1391

- Add test folder to vmaas/common, update module names
  ([`a523b80`](https://github.com/RedHatInsights/vmaas/commit/a523b802d97d907fb082ebacad6ab5673a040ff0))

rename modules not to conflict with 3rd party libs names - VMAAS-1391

- Added testing SQLite cache script, updated test_cache.py
  ([`270dae4`](https://github.com/RedHatInsights/vmaas/commit/270dae4a8020ff03c5216084159db5bca883090f))

- VMAAS-1391

- Cleanup yaml_cache.py, remove useless commented code
  ([`9b6b616`](https://github.com/RedHatInsights/vmaas/commit/9b6b616b9862ca1bd1b512358f95a037cabf6262))

- VMAAS-1391

- **webapp**: Added /pkglist endpoint tests
  ([`ca6f867`](https://github.com/RedHatInsights/vmaas/commit/ca6f867c6651f0d7eec51ef40a7c49dc252a4480))

- VMAAS-1391

### Features

- Added common/algorithms.py module with find_index method
  ([`1431ee2`](https://github.com/RedHatInsights/vmaas/commit/1431ee24bad99a38531fd048d5b22df0e4cc70fa))

- VMAAS-1391

- **webapp**: Add "package_detail.modified" attribute and modified index to cache
  ([`50b1e4d`](https://github.com/RedHatInsights/vmaas/commit/50b1e4d642af0aa1add880de19e43be7f97ef863))

- add modified as int timestamp to store into int array (package_detail) - add modified index to
  cache to support "modified_since" argument - VMAAS-1391

- **webapp**: Add new /pkglist endpoint
  ([`a542839`](https://github.com/RedHatInsights/vmaas/commit/a542839164d4251bbc03355f99e7634e4ec29f82))

- VMAAS-1391

- **webapp**: Update api spec with /pkglist endpoint
  ([`0b4aa64`](https://github.com/RedHatInsights/vmaas/commit/0b4aa645d2eb74022366fe7c325cde9b8cb02cd7))

- VMAAS-1391


## v2.31.2 (2021-10-27)

### Bug Fixes

- **reposcan**: Skip populating empty repo data
  ([`b7a11b3`](https://github.com/RedHatInsights/vmaas/commit/b7a11b380dd4491d9b24eda4fb3c84af073c1ece))

VMAAS-1378


## v2.31.1 (2021-10-27)

### Bug Fixes

- Update deps
  ([`3afb539`](https://github.com/RedHatInsights/vmaas/commit/3afb53966ca4567ba76fc8dd2eff84909f006685))

- VMAAS-1393

- Updated lint related things
  ([`0ceacf8`](https://github.com/RedHatInsights/vmaas/commit/0ceacf839df8c687adb04c38e6b1dcd65a5c2290))

- VMAAS-1393

- **reposcan**: Fixed implicit json serialization warning
  ([`7cb9ca0`](https://github.com/RedHatInsights/vmaas/commit/7cb9ca0c807da85b941c374f10a3f0c88fafb0a7))

- in health handler - vmaas/reposcan/test/test_reposcan.py::TestReposcanApp::test_monitoring_health
  /var/lib/pgsql/.local/share/virtualenvs/vmaas-HvggfB72/lib/python3.6/site-packages/connexion/apis/flask_api.py:199:
  FutureWarning: Implicit (flask) JSON serialization will change in the next major version. This is
  triggered because a response body is being serialized as JSON even though the mimetype is not a
  JSON type. This will be replaced by something that is mimetype-specific and may raise an error
  instead of silently converting everything to JSON. Please make sure to specify media/mime types in
  your specs. FutureWarning # a Deprecation targeted at application users. - VMAAS-1393

### Chores

- Make cpu limit configurable
  ([`b919f43`](https://github.com/RedHatInsights/vmaas/commit/b919f43453d7ae9370f188bc065d674efe0198b3))


## v2.31.0 (2021-10-21)

### Features

- **reposcan**: Sql updates - added package.modified timestamp column
  ([`08d2b6a`](https://github.com/RedHatInsights/vmaas/commit/08d2b6a877afe2644383c5e6bae8cace179c97dd))

VMAAS-1391

- **reposcan**: Updated package_store test, dump exporter and its tests
  ([`5debe20`](https://github.com/RedHatInsights/vmaas/commit/5debe20a723e7ed063b21e0a7cf36ac7a4b7e7a5))

VMAAS-1391

- **webapp**: Exclude modified from cache for now
  ([`c4de51c`](https://github.com/RedHatInsights/vmaas/commit/c4de51cd07e844e4e9770940afc5b77f4551fd4d))


## v2.30.0 (2021-10-07)

### Features

- **webapp**: Enhance /vulnerabilities API
  ([`613125d`](https://github.com/RedHatInsights/vmaas/commit/613125d640769bcb9f556a161c52ce0261bd4597))

VMAAS-1382

* adding new manually_fixable_cve_list containing extra CVEs reported by OVAL * adding extended mode
  to return also affected packages and advisories (more attributes may be added later) * obsoleting
  oval and oval_only modes

### Testing

- Response schema changes
  ([`ab62a00`](https://github.com/RedHatInsights/vmaas/commit/ab62a00d7c9c6770944ee50eb39733683af82e75))


## v2.29.0 (2021-10-07)

### Features

- **webapp**: Enable optimistic updates for /vulnerabilities
  ([`d7c1fe0`](https://github.com/RedHatInsights/vmaas/commit/d7c1fe03ffff9089dd615e8b028b0ecab8eb309c))

VMAAS-1386


## v2.28.4 (2021-10-07)

### Bug Fixes

- **webapp**: Load as many tables as possible even when dump is not up to date
  ([`751989b`](https://github.com/RedHatInsights/vmaas/commit/751989b6c9256575ac3071fae6bee93be9a4ae9b))


## v2.28.3 (2021-10-06)

### Bug Fixes

- **webapp**: Fix /pkgtree third-party repos info and third-party flag
  ([`717d79c`](https://github.com/RedHatInsights/vmaas/commit/717d79c820ed3e7f6b021b58b9cac7501b07225e))

- Include third-party package repositories - not included before - Exclude package with third-party
  repositories if needed - VMAAS-1351


## v2.28.2 (2021-10-05)

### Bug Fixes

- **webapp**: Fix /pkgtree endpoint when "modified_since" used
  ([`0f1d73e`](https://github.com/RedHatInsights/vmaas/commit/0f1d73ed3542b94a4cfa35156e941a338e7a7f6d))

- Exclude packages without time info (without errata) when "modified_since" used in request

VMAAS-1346

### Chores

- Use labels in pr_check
  ([`1155152`](https://github.com/RedHatInsights/vmaas/commit/1155152a9fbb13f8095a23835b1622008c01fdfb))

VULN-1948


## v2.28.1 (2021-09-17)

### Bug Fixes

- Set timeout for requests while waiting for services
  ([`ab4cb40`](https://github.com/RedHatInsights/vmaas/commit/ab4cb40b791df2e5f9558da664428574c1e9fad5))

requests will hang if no timeout is set which causes unnecessary pod restarts just after deploy

### Chores

- Don't wait for websocket in init container
  ([`65b4d41`](https://github.com/RedHatInsights/vmaas/commit/65b4d4197c24d0801e45504c1ded43498ab4f951))

- Repolist for multicontext module tests
  ([`99403a8`](https://github.com/RedHatInsights/vmaas/commit/99403a8f1e911599be992a5e9b3cf4677f578d95))

VMAAS-1383


## v2.28.0 (2021-09-14)

### Bug Fixes

- Silence pytest warnings
  ([`c71b03a`](https://github.com/RedHatInsights/vmaas/commit/c71b03ad08223bdff772dc895aeca3c70ed13431))

test_repository_store.py:57: PytestUnknownMarkWarning: Unknown pytest.mark.first - is this a typo?
  You can register custom marks to avoid this warning - for details, see
  https://docs.pytest.org/en/stable/mark.html

- Update developer setup to single app layout
  ([`9810bc2`](https://github.com/RedHatInsights/vmaas/commit/9810bc2ea42165ed9cd1c4005dbd45a344e95db2))

### Chores

- Allow build on aarch64
  ([`5ba778f`](https://github.com/RedHatInsights/vmaas/commit/5ba778f4aa03c354bfa72fe80d6c8c5c96bf0327))

- Remove unused MANIFEST_* params
  ([`434a9aa`](https://github.com/RedHatInsights/vmaas/commit/434a9aa37a38be624b0d151086d817746d882128))

- Signal handler takes 2 argmuents
  ([`b37e22d`](https://github.com/RedHatInsights/vmaas/commit/b37e22dced31ebf3758218f8b3e050b305c93936))

- **clowder**: Add proxy for reposcan-service
  ([`5fe1ac1`](https://github.com/RedHatInsights/vmaas/commit/5fe1ac113f795a55c60a9cbfb5d819848c9b33ce))

### Features

- Delete stream requires when stream is deleted
  ([`db18b59`](https://github.com/RedHatInsights/vmaas/commit/db18b59c88057cd7ba9462a3b17e2d2ff2c1a1bf))

- Export module requires data
  ([`77b48c6`](https://github.com/RedHatInsights/vmaas/commit/77b48c61e4b8cb65a145a2d24e2db8c3d45fce47))

- Fiter out module stream without satisfied requires
  ([`b0821bc`](https://github.com/RedHatInsights/vmaas/commit/b0821bc3982ded9111e1cb1d841703be0345fad9))

- Improve exporter test form module requires
  ([`dd79c7c`](https://github.com/RedHatInsights/vmaas/commit/dd79c7c3304167280fff939e67272f1df0784196))

- Read module requires into cache
  ([`3b4afc7`](https://github.com/RedHatInsights/vmaas/commit/3b4afc72cb875a3200529f1cc288f3f5befa1e7e))

- Store module requires during reposcan
  ([`8487e65`](https://github.com/RedHatInsights/vmaas/commit/8487e65d70f8d0ed1357177d734aab2b7af52e37))

- Table to store module dependencies
  ([`24f3a25`](https://github.com/RedHatInsights/vmaas/commit/24f3a25a0f85edb8c5fc0164832302546e9711eb))

- Updated test for module loading
  ([`e98fca9`](https://github.com/RedHatInsights/vmaas/commit/e98fca94b3307884f10dd7e3c7feee27c9d9433f))


## v2.27.2 (2021-09-07)

### Bug Fixes

- **test**: Fix pur deps to fix AttributeError: 'bool' object has no attribute 'lower'
  ([`1d73e3b`](https://github.com/RedHatInsights/vmaas/commit/1d73e3b92619afd15d7eb267cbcf869852c8cebe))

fixing Traceback (most recent call last): File
  "/var/lib/pgsql/.local/share/virtualenvs/vmaas-HvggfB72/bin/pur", line 8, in <module>
  sys.exit(pur()) ... File
  "/var/lib/pgsql/.local/share/virtualenvs/vmaas-HvggfB72/lib/python3.6/site-packages/pur/__init__.py",
  line 54, in convert if value.lower() == 'true': AttributeError: 'bool' object has no attribute
  'lower'

- **test**: Fixing new pylint warnings
  ([`024e118`](https://github.com/RedHatInsights/vmaas/commit/024e1186e7534ff7f38a22fda2ee64e11e8bec43))

W1514: Using open without explicitly specifying an encoding (unspecified-encoding)

C0206: Consider iterating with .items() (consider-using-dict-items)

R1735: Consider using {} instead of dict() (use-dict-literal)

R1732: Consider using 'with' for resource-allocating operations (consider-using-with)

W0612: Unused variable 'err' (unused-variable)

R0402: Use 'from vmaas.common import rpm' instead (consider-using-from-import)

### Build System

- Disable unnecessary repos
  ([`6a3ed7d`](https://github.com/RedHatInsights/vmaas/commit/6a3ed7d8b014b1d36eb2fa315b67c65b20c17fee))

- Remove workaround for postgresql installation
  ([`374225e`](https://github.com/RedHatInsights/vmaas/commit/374225e47046e45b63b16094b73bf50bf48fcccd))


## v2.27.1 (2021-09-07)

### Bug Fixes

- **reposcan**: Fixed advisory "reboot_suggested" value parsing
  ([`85c1ddd`](https://github.com/RedHatInsights/vmaas/commit/85c1ddda23531c9118a7000d711cabae99c47eef))

VMAAS-1365


## v2.27.0 (2021-09-06)

### Features

- **reposcan**: Added 'requires_reboot' to dump exporter
  ([`309f35e`](https://github.com/RedHatInsights/vmaas/commit/309f35e2d3f6c097c432cac7429dbff4cf905dca))

VMAAS-1365

- **reposcan**: Added option to disable some sync parts (git, cve, oval...)
  ([`f38da8e`](https://github.com/RedHatInsights/vmaas/commit/f38da8e14de4143bde3fd310f75166a79f8bc1aa))

VMAAS-1365

- **webapp**: Added 'requires_reboot' to api docs (v3)
  ([`32440f2`](https://github.com/RedHatInsights/vmaas/commit/32440f2be2bc98fed7486e6dc1f0383923e2cb15))

VMAAS-1365

- **webapp**: Added 'requires_reboot' to webapp
  ([`f222500`](https://github.com/RedHatInsights/vmaas/commit/f2225000eef4c7a632649ae87695de451d91f6eb))

VMAAS-1365

updated tests, updated testing cache data


## v2.26.1 (2021-09-06)

### Bug Fixes

- **webapp**: Fix /updates test for arch "(none)"
  ([`c24be27`](https://github.com/RedHatInsights/vmaas/commit/c24be272d61c2e385efbfd9da176c70ae58434bd))

VMAAS-1375

It was failing when used with third_party and optimistic_updates


## v2.26.0 (2021-09-03)

### Chores

- **clowder**: Smooth transition with legacy ports
  ([`d06a7aa`](https://github.com/RedHatInsights/vmaas/commit/d06a7aa7f1e802d2d47fca005f79974b7b059ebd))

VULN-1909

### Features

- **reposcan**: Auto delete old oval items
  ([`38322bf`](https://github.com/RedHatInsights/vmaas/commit/38322bf6cd48585387d8e25d51f4bf5c7d669988))

VMAAS-1332


## v2.25.0 (2021-09-01)

### Bug Fixes

- **database**: Add missing file_id foreign key
  ([`a6a23a9`](https://github.com/RedHatInsights/vmaas/commit/a6a23a95feb45a9560fd580ad84f095b6b1a6019))

- **reposcan**: Disable rhel-7-alt OVAL stream
  ([`2ea9987`](https://github.com/RedHatInsights/vmaas/commit/2ea99875f6038b7fad13fc66e07a2aadf9f45e18))

VMAAS-1373

see also
  https://github.com/quay/claircore/commit/baff66333b025d863779cea58e1a5aedd22a4bb3#diff-2f9b764af2192de1953c5744b05da6f02f259381069047cf2cc8e718fdec3b4f

### Build System

- Remove generate_manifest.sh and deps.
  ([`b672578`](https://github.com/RedHatInsights/vmaas/commit/b672578cc79d29359a721453791f11ed7f6ba2f7))

### Chores

- Add rhel8 baseos testing data
  ([`39e468b`](https://github.com/RedHatInsights/vmaas/commit/39e468b04bfe2c302ff00e8c924962f90b06294b))

- Change memory limits in webapp
  ([`4965608`](https://github.com/RedHatInsights/vmaas/commit/4965608a1f5fb1f4f93b66b8b6a985230f888288))

VULN-1906

- Improve image build
  ([`0dc8cd2`](https://github.com/RedHatInsights/vmaas/commit/0dc8cd27468afa41928e4d5caf32b120b2b12490))

VULN-1824

### Features

- Implement requires_reboot flag for advisories
  ([`4a58f6d`](https://github.com/RedHatInsights/vmaas/commit/4a58f6d2d6c76b289d3b1e22aca2fcd0a377679e))

- **reposcan**: Automatically delete filtered/obsolete OVAL streams
  ([`bd977e2`](https://github.com/RedHatInsights/vmaas/commit/bd977e210c33a955ef23d0ab8bb7cf5e56533498))

VMAAS-1332

- **reposcan**: Support deleting OVAL files
  ([`a499029`](https://github.com/RedHatInsights/vmaas/commit/a49902903fbe075f68aa16dbae3a8bb8c50a9b45))

VMAAS-1332


## v2.24.1 (2021-07-28)

### Bug Fixes

- **clowder**: Use rds ca path
  ([`9f8a568`](https://github.com/RedHatInsights/vmaas/commit/9f8a5684d3dc02641d59926f31e1f4d975ecc274))

### Chores

- Jenkins is replaced by gh action/app-sre pr_check
  ([`a0a6285`](https://github.com/RedHatInsights/vmaas/commit/a0a6285070f9f1195033963c15c6c978511b02e9))

- Run smoke tests using cji
  ([`081a2ac`](https://github.com/RedHatInsights/vmaas/commit/081a2ac0b3263aac7ad1378f7395ede5c5c5df63))

VULN-1742


## v2.24.0 (2021-07-15)

### Features

- **reposcan**: Support filtering OVAL files
  ([`29d555c`](https://github.com/RedHatInsights/vmaas/commit/29d555c7c67939e3e37eb3840935bc590b426450))

put a warning in a log


## v2.23.6 (2021-07-14)

### Bug Fixes

- **reposcan**: Fix slow re-syncs due to missing index
  ([`e9c9499`](https://github.com/RedHatInsights/vmaas/commit/e9c9499970d15a5c5e99be756982ad566724eff4))

### Chores

- Clean unnecessary things from clowdapp
  ([`2840010`](https://github.com/RedHatInsights/vmaas/commit/284001088cc358cadf632bda23576c49ffa63038))

- Unify logging - use format from vuln-engine
  ([`f0f7679`](https://github.com/RedHatInsights/vmaas/commit/f0f7679f2d2bfacffb025a184a67df9439e9d6e0))

- Use github-vmaas-bot instead of vulnerability-bot
  ([`fb64e96`](https://github.com/RedHatInsights/vmaas/commit/fb64e9648fcca7cccfbd29bde4c74b6c8fe59a25))

- Use github-vulnerability-bot secret from epehemeral-base
  ([`bbcdbde`](https://github.com/RedHatInsights/vmaas/commit/bbcdbde1fee6aa634f05ce7de415561af9ebeeff))

### Refactoring

- Migrate from configmap to deployment
  ([`f3b6f31`](https://github.com/RedHatInsights/vmaas/commit/f3b6f31b60348e7aa6594b3af9cbc96e36649783))


## v2.23.5 (2021-07-12)

### Bug Fixes

- **reposcan**: Products being a list instead of dict in reposcan
  ([`cfba1fd`](https://github.com/RedHatInsights/vmaas/commit/cfba1fd69cd94af0a2c08aa458075f904e3b6bc3))

### Chores

- Fix pylint issue, explicit check param is recommended
  ([`8e5ced5`](https://github.com/RedHatInsights/vmaas/commit/8e5ced53cc3fc4d08fc9a3d4b2edddc0fd891d3c))


## v2.23.4 (2021-07-12)

### Bug Fixes

- Check=true throws subprocess.CalledProcessError in case of non-zero return code
  ([`cf4cee5`](https://github.com/RedHatInsights/vmaas/commit/cf4cee5e5bf164c9774e9c4ac64feb03b13b3284))

### Chores

- **clowder**: Respect resource requests/limits in ephemeral
  ([`b76c43c`](https://github.com/RedHatInsights/vmaas/commit/b76c43c351df588fb50208c7e25983cbf5a09d40))


## v2.23.3 (2021-07-01)

### Bug Fixes

- **reposcan**: Remove parenthesis from returning statement
  ([`7e54a90`](https://github.com/RedHatInsights/vmaas/commit/7e54a904eeefc11473251ab1c3fc4f614019c8a3))


## v2.23.2 (2021-07-01)

### Bug Fixes

- **database**: Set ON_ERROR_STOP=on to have non-zero RC when error occurs, also don't rely on
  stderr
  ([`1046e97`](https://github.com/RedHatInsights/vmaas/commit/1046e976680670245eb40ce5f10ed946003b1de7))

notices from truncate command are printed to stderr

### Chores

- Faster table cleanup during migration
  ([`177115d`](https://github.com/RedHatInsights/vmaas/commit/177115d83b09b9a4a4c92d1b62f4b00bbcfaf761))


## v2.23.1 (2021-07-01)

### Bug Fixes

- **database**: Apply migration file as single transaction
  ([`c64d11f`](https://github.com/RedHatInsights/vmaas/commit/c64d11f7b14411834657a29710ce1d0083976374))


## v2.23.0 (2021-07-01)

### Chores

- Improve cleanup speed during migration
  ([`4fb3f1e`](https://github.com/RedHatInsights/vmaas/commit/4fb3f1e4a3ca7e1627a0a4525c738946122fd57d))

### Features

- **database**: Bump database to rhel8/centos8
  ([`8fc0b23`](https://github.com/RedHatInsights/vmaas/commit/8fc0b23953cb5a97f8accbca057e14f6dd223fd0))


## v2.22.1 (2021-07-01)

### Bug Fixes

- **database**: Re-structure OVAL-file associations
  ([`c3e2d6b`](https://github.com/RedHatInsights/vmaas/commit/c3e2d6b8374c5d91b91d1f616c840abc82fd9110))

- **reposcan**: Detect changes in oval files better
  ([`c69017a`](https://github.com/RedHatInsights/vmaas/commit/c69017a17f14a2ebdf7e3342bf1cab0d05eba906))

improves incremental updates where oval_id can change

- **reposcan**: Sync OVAL data into updated schema
  ([`8a39630`](https://github.com/RedHatInsights/vmaas/commit/8a39630b6d6c5e5bc4e4da655157c4a3c7a91622))

### Chores

- Remove vmaas-reposcan-tmp persistent storage
  ([`67e9e35`](https://github.com/RedHatInsights/vmaas/commit/67e9e35dee0a458bb754738774fe03020108757d))


## v2.22.0 (2021-06-17)

### Features

- **reposcan**: Accept multiple repolists for git sync
  ([`f85f4a0`](https://github.com/RedHatInsights/vmaas/commit/f85f4a01b206063b1221de8853b5ce92aa6b30d0))


## v2.21.0 (2021-06-10)

### Chores

- Deploy vmaas component of vulnerability app
  ([`86ddd51`](https://github.com/RedHatInsights/vmaas/commit/86ddd51ef9fac28cb2c84c28b37dd32a4d02c0a7))

### Features

- **reposcan**: Retry periodic cache dump later if it failed
  ([`0694e3a`](https://github.com/RedHatInsights/vmaas/commit/0694e3a9f6c15164eeeedd4ce8b918704224681d))


## v2.20.2 (2021-06-09)

### Bug Fixes

- Bump app_common_python to get sslMode
  ([`b76eb7f`](https://github.com/RedHatInsights/vmaas/commit/b76eb7f8c70b245da94f5007825b034ec6d4daa5))

- Default ssl mode can't be empty string
  ([`17a366e`](https://github.com/RedHatInsights/vmaas/commit/17a366e40246c9a9106e06824a4abcccc6cff5f7))


## v2.20.1 (2021-06-08)

### Bug Fixes

- **webapp**: Revert: add "modified_since" to /v3/pkgtree response"
  ([`ae15ba0`](https://github.com/RedHatInsights/vmaas/commit/ae15ba02709fca396a6b678fdfdb84f4d0b35ade))

This reverts commit aee93a6a20d1bee6a9f4af45d07e1ae6d399c79a.


## v2.20.0 (2021-06-02)

### Chores

- Add script to easily re-generate Pipfile.lock
  ([`3616dd5`](https://github.com/RedHatInsights/vmaas/commit/3616dd5c940d95f4c65d70fb6c02b4e6e7070616))

- Fix new pylint issues
  ([`ce92d78`](https://github.com/RedHatInsights/vmaas/commit/ce92d78856f15ec9f5ce26d728fe299326e3381e))

- Podman bindings are not needed + re-gen lock file
  ([`acee9ef`](https://github.com/RedHatInsights/vmaas/commit/acee9ef3d2d14de58390d45359c1748fe9cc00cc))

### Features

- Set PostgreSQL SSL mode
  ([`b5a555f`](https://github.com/RedHatInsights/vmaas/commit/b5a555f983e32dcb33be29a1a01f3f9b5e5cb32a))

### Refactoring

- **webapp**: Make responses more consistent
  ([`00447bb`](https://github.com/RedHatInsights/vmaas/commit/00447bb331347c3ec1c7502a198b794edc95fa43))


## v2.19.2 (2021-05-25)

### Bug Fixes

- **webapp**: Add "modified_since" to /v3/pkgtree response
  ([`aee93a6`](https://github.com/RedHatInsights/vmaas/commit/aee93a6a20d1bee6a9f4af45d07e1ae6d399c79a))


## v2.19.1 (2021-05-25)

### Bug Fixes

- **webapp**: Comparison between srt and int, enhance split the string to int/str parts
  ([`315fee8`](https://github.com/RedHatInsights/vmaas/commit/315fee89628156b83956ddf71df928896d34ee89))

same logic as storing evr_t type in postgres

e.g. failure in comparing microcode_ctl-4:20180807a-2.el8.x86_64 and
  microcode_ctl-4:20200609-2.20210216.1.el8_3.x86_64

- **webapp**: If CVE is not in DB from cvemap, it's not connected with definition
  ([`d244df0`](https://github.com/RedHatInsights/vmaas/commit/d244df04e69c0b839f8674de9fc638890a0bb92c))


## v2.19.0 (2021-05-19)

### Features

- **reposcan**: Import OVAL module streams
  ([`0408efc`](https://github.com/RedHatInsights/vmaas/commit/0408efcec808297f09226c648eddb3f11f95279e))

- **webapp**: Filter modules_list in OVAL evaluation
  ([`ab8011f`](https://github.com/RedHatInsights/vmaas/commit/ab8011f443a16299aab4f11aaa20f132bd32bb35))


## v2.18.1 (2021-05-17)

### Bug Fixes

- **reposcan**: Fix path to wait script and replace it with python version
  ([`8d40e09`](https://github.com/RedHatInsights/vmaas/commit/8d40e097d31632f0eb505b8de960ede448376117))

### Chores

- Fix path in semantic release config
  ([`3d1fa21`](https://github.com/RedHatInsights/vmaas/commit/3d1fa210f96f5418d4a20448a2ccb95054cce32f))

- Reorganize project files as a Python project
  ([`fc690ee`](https://github.com/RedHatInsights/vmaas/commit/fc690ee74054c099853a3ff1f71c283266f442da))


## v2.18.0 (2021-05-14)

### Bug Fixes

- Export and load missing OVAL data
  ([`b02aa74`](https://github.com/RedHatInsights/vmaas/commit/b02aa74b80d0e87be8fb462100d9872ef1bb21ca))

- Move fetch_latest_dump out of DataDump
  ([`3b6eb9b`](https://github.com/RedHatInsights/vmaas/commit/3b6eb9bc0429187bcbd9f1c5e7fbc25db2e0ea39))

- Third_party support, fix repo/errata/cve structure, updates order, datetime format etc.
  ([`e0e44a6`](https://github.com/RedHatInsights/vmaas/commit/e0e44a68c2d0b045a7f2aa203c8c36abdccaeea5))

- **reposcan**: /data is mount point
  ([`a2c93b7`](https://github.com/RedHatInsights/vmaas/commit/a2c93b7f2fbd29bf313614b1ae45a4bd173a6400))

- **reposcan**: Fix the package_name query
  ([`27aff01`](https://github.com/RedHatInsights/vmaas/commit/27aff01d12af26cf3d428bcba28d10c93d955e97))

- **webapp**: Load as set() and array.array('q') where previously
  ([`828a5f8`](https://github.com/RedHatInsights/vmaas/commit/828a5f89b9cd7b11ea0dc64f40440628fa753586))

- **webapp**: Productid2repoids was removed
  ([`3e461ee`](https://github.com/RedHatInsights/vmaas/commit/3e461eebd010825061ce2a53e10a6f243af52887))

### Chores

- **reposcan**: Stop generating shelve dump and rewrite exporter test to use sqlite
  ([`86974d6`](https://github.com/RedHatInsights/vmaas/commit/86974d61c0325ab3f15ee7a63740c1b30a47f4ea))

- **webapp**: Start syncing sqlite file instead of shelve
  ([`526db5a`](https://github.com/RedHatInsights/vmaas/commit/526db5abc59fcbd3a51a453d0ba9f12849eb552f))

test data need to be re-generated to sqlite format

### Features

- Add sqlite database format
  ([`eedcd53`](https://github.com/RedHatInsights/vmaas/commit/eedcd5330546a53f19894d621c3099b69ec0009c))

Extract sqlite dump generation code from the semtezv/next branch

- **webapp**: Return HTTP 503 when no dump is loaded
  ([`5b7002a`](https://github.com/RedHatInsights/vmaas/commit/5b7002a968c1a12ca7a51c58b9fe1a3e7020468a))


## v2.17.0 (2021-05-12)

### Features

- **reposcan**: Allow repolists to opt_out of default certificates
  ([`dc00b21`](https://github.com/RedHatInsights/vmaas/commit/dc00b215c1b4d4283f87f9b63a02fa26fcc27aa1))


## v2.16.0 (2021-05-12)

### Features

- **reposcan**: Accept lists for content set data
  ([`24be17e`](https://github.com/RedHatInsights/vmaas/commit/24be17ec2ae0ef344eca161556c617cefa95669b))


## v2.15.2 (2021-05-05)

### Bug Fixes

- **webapp**: Default to false until it's well tested, apps can request it anyway using param
  ([`646b3f6`](https://github.com/RedHatInsights/vmaas/commit/646b3f683a2e5eafd33a2750e0895aa8c4f153bd))


## v2.15.1 (2021-05-04)

### Bug Fixes

- **webapp**: Add more as_long_arr casts
  ([`17d5137`](https://github.com/RedHatInsights/vmaas/commit/17d513726b333445bcbfb012d1c6b0cd913cc100))

- **webapp**: Productid2repoids is not used
  ([`9483f9d`](https://github.com/RedHatInsights/vmaas/commit/9483f9dc18f113491b1371f472733f0a7c745691))


## v2.15.0 (2021-05-04)

### Bug Fixes

- **webapp**: Warn but don't crash
  ([`8f4c0c2`](https://github.com/RedHatInsights/vmaas/commit/8f4c0c294fd877a3e4ec26dac6b92f07db8a1079))

### Features

- **reposcan**: Export OVAL data
  ([`49b1ec4`](https://github.com/RedHatInsights/vmaas/commit/49b1ec461b8a37d82e2c4fc7edb3b0a714e48cf7))

- **webapp**: Evaluate OVAL
  ([`06db2b1`](https://github.com/RedHatInsights/vmaas/commit/06db2b17148e10e3828a065401b57e3baf9800f9))


## v2.14.1 (2021-04-29)

### Bug Fixes

- **reposcan**: Fix KeyError when importing new repos
  ([`9303d34`](https://github.com/RedHatInsights/vmaas/commit/9303d347c364757e2af715321c53fb6415939c45))


## v2.14.0 (2021-04-28)

### Bug Fixes

- **reposcan**: Sync CPE substrings from OVAL files
  ([`605d020`](https://github.com/RedHatInsights/vmaas/commit/605d020a28a8bbaf67f043e24507d87e8739af11))

- **reposcan**: Sync missing package names and EVRs
  ([`5079858`](https://github.com/RedHatInsights/vmaas/commit/507985819d9b6940debdf5b33080b32762743cbb))

### Features

- **reposcan**: Warn about extra repos in DB when syncing main repolist from git
  ([`5c5693d`](https://github.com/RedHatInsights/vmaas/commit/5c5693df8afc88d9bca0acb6924853ad754b78bc))


## v2.13.2 (2021-04-28)

### Bug Fixes

- **reposcan**: Delete from new dependent tables
  ([`ebcb5cb`](https://github.com/RedHatInsights/vmaas/commit/ebcb5cb83f58dd0342c9c12dc8ce745e5829c0f0))

- **reposcan**: Optimize content deletion speed
  ([`b5fee66`](https://github.com/RedHatInsights/vmaas/commit/b5fee6630ec249bd89ee4b82da0edb875902edb6))

### Chores

- Add cached epel repolist for tests
  ([`685c3a3`](https://github.com/RedHatInsights/vmaas/commit/685c3a3f5c8614dd61cd65a1a3a5e76866848089))


## v2.13.1 (2021-04-21)

### Bug Fixes

- **webapp**: Include packages without errata
  ([`4b4e409`](https://github.com/RedHatInsights/vmaas/commit/4b4e409769dd14864f8275f51118beda159fa4d8))


## v2.13.0 (2021-04-20)

### Chores

- Update to current manifest format
  ([`76bc06c`](https://github.com/RedHatInsights/vmaas/commit/76bc06cc81ed5bd7ab3784d425b1f2221e0d716a))

### Features

- **webapp**: Add "modified_since" support to /pkgtree v3
  ([`922c84b`](https://github.com/RedHatInsights/vmaas/commit/922c84bab2dc2af861f1d6cba362dc6dc58cc887))


## v2.12.0 (2021-04-20)

### Features

- **webapp**: Add new /pkgtree endpoint options
  ([`5811f2f`](https://github.com/RedHatInsights/vmaas/commit/5811f2f6da52c8fbf192ce01944b230bb3a1d2bb))


## v2.11.0 (2021-04-19)

### Chores

- Fix docker run in ci.yml
  ([`fe8eb4e`](https://github.com/RedHatInsights/vmaas/commit/fe8eb4e4d0ab9c61c6df4efd487387b16e02f4f6))

- Reposcan with env var in gh action
  ([`5997fed`](https://github.com/RedHatInsights/vmaas/commit/5997fed305e9998dbff4c6044816185865d6b38d))

- Sync cached oval in gh actions
  ([`8798f23`](https://github.com/RedHatInsights/vmaas/commit/8798f23d73d9fb6b3c8a019c1b7be78015b1927c))

### Features

- **webapp**: Added summary and description info to /pkgtree response v3
  ([`909d7c3`](https://github.com/RedHatInsights/vmaas/commit/909d7c36368e003c616f21acff8df34204928929))


## v2.10.0 (2021-04-16)

### Chores

- Remove integration tests on osd3
  ([`fec4f97`](https://github.com/RedHatInsights/vmaas/commit/fec4f9755c2d3c32b3d33b4a8d1f166efbe6ce6f))

- Set OVAL feed in clowdapp and gh actions
  ([`cdd59aa`](https://github.com/RedHatInsights/vmaas/commit/cdd59aae15db504f2392ecec091ac433bdcbefcc))

- Use iqe-vmaas-plugin
  ([`02956eb`](https://github.com/RedHatInsights/vmaas/commit/02956eb4facc89c257b4df8db9dd0abf7d9f66fc))

- **webapp**: Cleaned pkgtree.py code
  ([`6229604`](https://github.com/RedHatInsights/vmaas/commit/6229604a6010550354305defd991b90b1afa57d1))

### Features

- **webapp**: Added pagination to /pkgtree (api_version=3)
  ([`568497d`](https://github.com/RedHatInsights/vmaas/commit/568497df7f29fa139c0544a863c525a613110ba4))


## v2.9.0 (2021-04-15)

### Features

- **reposcan**: Add support for different git repolist branches
  ([`d7f8446`](https://github.com/RedHatInsights/vmaas/commit/d7f8446b35ad08ded908bd95d9e718ea1991b33a))


## v2.8.2 (2021-04-08)

### Bug Fixes

- **webapp**: Close dbm after loading cache
  ([`e6aad5c`](https://github.com/RedHatInsights/vmaas/commit/e6aad5c3f3e34527dd74ab347d5a272170d337b3))

### Chores

- Don't push qa image tag in build_deploy
  ([`154080f`](https://github.com/RedHatInsights/vmaas/commit/154080fca22685a1b10feb53939937d563313c9a))


## v2.8.1 (2021-04-08)

### Bug Fixes

- **reposcan**: Empty insert
  ([`49022a4`](https://github.com/RedHatInsights/vmaas/commit/49022a415a964999b5ac45097f15c96d98be3990))

- **reposcan**: Import CPEs even if not found in CPE dict
  ([`fba7ffb`](https://github.com/RedHatInsights/vmaas/commit/fba7ffb5e83ec89ce3d128cd5d40f3715e8df9da))


## v2.8.0 (2021-04-08)

### Features

- **reposcan**: Support cleaning /tmp manually
  ([`504aa3d`](https://github.com/RedHatInsights/vmaas/commit/504aa3dd34839ee9b281b566c8f90ee711f80aef))


## v2.7.1 (2021-04-07)

### Bug Fixes

- **reposcan**: Handling of repolist urls
  ([`de3b8a0`](https://github.com/RedHatInsights/vmaas/commit/de3b8a0595bb5d0ff95d63258100ba47ab4a5445))

### Chores

- /rebase command for PRs
  ([`6597f3b`](https://github.com/RedHatInsights/vmaas/commit/6597f3b3e9e9db13b87fc45f0bf55fd4d1fedb7d))


## v2.7.0 (2021-04-06)

### Features

- **webapp**: Third party content support - Webapp
  ([`c001a8d`](https://github.com/RedHatInsights/vmaas/commit/c001a8db08efde47786ddcd119adf314288b5fea))

Signed-off-by: mhornick <mhornick@redhat.com>


## v2.6.0 (2021-04-06)

### Chores

- Refactor and mirror health endpoint for clowder
  ([`30aa9ad`](https://github.com/RedHatInsights/vmaas/commit/30aa9ad17ae09f2e4d022f2c1c99501ed620d7d8))

### Features

- **reposcan**: Download OVAL files to tmp dir and unpack
  ([`737c0f3`](https://github.com/RedHatInsights/vmaas/commit/737c0f33baf748e2ee84561eeba5cadd26ec72b6))

- **reposcan**: Parse and store OVAL data
  ([`c66d0e4`](https://github.com/RedHatInsights/vmaas/commit/c66d0e46931148a9dd57a14819b6d60f8d3be0b9))

- **reposcan**: Register sync API for OVAL files
  ([`9673f42`](https://github.com/RedHatInsights/vmaas/commit/9673f4224f06a1cd78a007f941a32cea113d4407))


## v2.5.0 (2021-03-29)

### Features

- **reposcan**: Third-party content support, reposcan
  ([`7d203aa`](https://github.com/RedHatInsights/vmaas/commit/7d203aa6beb56a68d9e2338615472a89548e3e94))


## v2.4.1 (2021-03-26)

### Bug Fixes

- **webapp**: Fixed asserts in test_updates.py
  ([`f31e3dc`](https://github.com/RedHatInsights/vmaas/commit/f31e3dc3047a8a5d0edabbc4d32bdb9c1ad5332d))

modified the input to get some real updates


## v2.4.0 (2021-03-23)

### Chores

- Update aiohttp to fix CVE-2021-21330
  ([`e110a63`](https://github.com/RedHatInsights/vmaas/commit/e110a63849cda0d08196ecd6472eb614fc4b7a5d))

### Features

- **webapp**: Define interface for patched/unpatched CVEs and OVAL evaluation toggles
  ([`125c839`](https://github.com/RedHatInsights/vmaas/commit/125c8397041c138b09c611d19095258151321aae))


## v2.3.0 (2021-03-18)

### Chores

- Add GH releases badge
  ([`c3e8f8c`](https://github.com/RedHatInsights/vmaas/commit/c3e8f8c394d69a4150bab8ecae2637afc67d0e4e))

- Change Travis badge to GH Actions
  ([`3398072`](https://github.com/RedHatInsights/vmaas/commit/3398072effd0f15daf489cd7d44fc18a0a893dc2))

- Use turnpike to sync repolist
  ([`52f856f`](https://github.com/RedHatInsights/vmaas/commit/52f856fa56ac4bd73c573f2171793f0c92090cfc))

- **reposcan**: Remove unused variable
  ([`6b48270`](https://github.com/RedHatInsights/vmaas/commit/6b482700d48518b51763647d6163e6bc62ec923e))

### Features

- **database**: Introduce cpe tables
  ([`8247fde`](https://github.com/RedHatInsights/vmaas/commit/8247fded0468b7f19846b8d3827cdc13c1935bba))

- **reposcan**: Export imported CPE metadata
  ([`c1e441b`](https://github.com/RedHatInsights/vmaas/commit/c1e441bed7cc4e73c47fe203da7790d3c6545cc2))

- **reposcan**: Sync CPE metadata into DB
  ([`b688f9f`](https://github.com/RedHatInsights/vmaas/commit/b688f9f8eeee1d766a3b41c1e6c45978c6fd22f9))

- **webapp**: Show CPEs in /repos API
  ([`e080845`](https://github.com/RedHatInsights/vmaas/commit/e080845f5a3523f851dea20711fabd4a5f16ad0e))


## v2.2.1 (2021-03-08)

### Bug Fixes

- Waiting for DB and rsync port in e2e-deploy and docker-compose
  ([`9aad355`](https://github.com/RedHatInsights/vmaas/commit/9aad35511be74ef0dfa74ca5b8c8a829b08da3db))


## v2.2.0 (2021-03-05)

### Features

- **clowder**: Integrate with clowder
  ([`e419895`](https://github.com/RedHatInsights/vmaas/commit/e419895249391f3a6c00f363435f97084ae2b215))


## v2.1.1 (2021-03-03)

### Bug Fixes

- **reposcan**: Replace github auth with turnpike
  ([`d0e5a4f`](https://github.com/RedHatInsights/vmaas/commit/d0e5a4f639fd00f9a9a5c12238ab1bb734526d87))

no complete authentication/authorization done here, we just parse&log header from turnpike

### Chores

- There is no fix for tornado vulnerability yet, disable this one check
  ([`fe4ec5f`](https://github.com/RedHatInsights/vmaas/commit/fe4ec5ff99935b42b44509a164df4b800e8e5198))

39462: tornado <=6.1 resolved (6.0.3 installed)!

All versions of package tornado are vulnerable to Web Cache Poisoning by using a vector called
  parameter cloaking. When the attacker can separate query parameters using a semicolon (;), they
  can cause a difference in the interpretation of the request between the proxy (running with
  default configuration) and the server. This can result in malicious requests being cached as
  completely safe ones, as the proxy would usually not see the semicolon as a separator, and
  therefore would not include it in a cache key of an unkeyed parameter. See CVE-2020-28476.

- Use redhat-actions/oc-installer
  ([`e416841`](https://github.com/RedHatInsights/vmaas/commit/e416841ee4cef85a619578c0c2a0df84c837ad33))

- **gh_action**: Correct path, install tar
  ([`a5a8582`](https://github.com/RedHatInsights/vmaas/commit/a5a8582d6dbfb87665876d3b5c6ff1d6e5f185ea))


## v2.1.0 (2021-01-28)

### Chores

- Bump vmaas major version
  ([`245aee5`](https://github.com/RedHatInsights/vmaas/commit/245aee5ec64cbb8283763f0187bcf8a88815994f))

- Standardize API versioning (v2/v3 available for all endpoints) and prepare new base path for
  3scale
  ([`8563363`](https://github.com/RedHatInsights/vmaas/commit/856336392b2ad9b33d7c474ab59cbb3e5e2d46b0))

- Update libs
  ([`ea5d3e2`](https://github.com/RedHatInsights/vmaas/commit/ea5d3e2b2c8d5c6b252f7eb9b9aba36e224f069d))


## v1.20.7 (2021-01-05)

### Bug Fixes

- **webapp**: Check if websocket is open before message is sent and ensure concurrency
  ([`6f529d1`](https://github.com/RedHatInsights/vmaas/commit/6f529d1a014441c7341bd89f32bc32fde728685f))

VMAAS-1315

asyncio: [ERROR] Task exception was never retrievedfuture: <Task finished
  coro=<Websocket._refresh_cache() done, defined at /vmaas/webapp/app.py:422>
  exception=AttributeError("'NoneType' object has no attribute 'send_str'",)>'Traceback (most recent
  call last):\n File "/vmaas/webapp/app.py", line 428, in _refresh_cache\n await
  self.report_version()\n File "/vmaas/webapp/app.py", line 476, in report_version\n await
  self.websocket.send_str(f"version
  {BaseHandler.db_cache.dbchange.get(\'exported\')}")\nAttributeError: \'NoneType\' object has no
  attribute \'send_str\''|


## v1.20.6 (2020-12-03)

### Bug Fixes

- **reposcan**: Skip repos with invalid sqlite database
  ([`35388b5`](https://github.com/RedHatInsights/vmaas/commit/35388b551c3de19f745f50451601e898c3b09b7b))


## v1.20.5 (2020-11-19)

### Bug Fixes

- Duplicate messages in kibana
  ([`a296cb9`](https://github.com/RedHatInsights/vmaas/commit/a296cb97cc6b2c4ad344f323ddbc3835963a9b01))

### Chores

- Re-lock dependencies
  ([`d279591`](https://github.com/RedHatInsights/vmaas/commit/d2795913d105b1ebcfceda913f0d197b5768bb7d))

- Replace Travis CI with Github Actions
  ([`c7843c1`](https://github.com/RedHatInsights/vmaas/commit/c7843c1148b1e6a66563830096965017f254f4e0))

- Update all dependencies
  ([`736fdfa`](https://github.com/RedHatInsights/vmaas/commit/736fdfa32e0e96e80baae0c4008823b71f0d809b))

This reverts commit d2795913d105b1ebcfceda913f0d197b5768bb7d.

### Testing

- Caret is now escaped in the response
  ([`a50f854`](https://github.com/RedHatInsights/vmaas/commit/a50f85455ab3e0b824cad70b80136b37c6c25fc9))


## v1.20.4 (2020-10-29)

### Bug Fixes

- Use pod name for log-stream in CW config
  ([`f03fed4`](https://github.com/RedHatInsights/vmaas/commit/f03fed4ff38fa50a6c1f414618759b724f8e3fc2))

### Chores

- Grafana in stage/prod was updated
  ([`e27d81d`](https://github.com/RedHatInsights/vmaas/commit/e27d81d9251217cd23174466fce8961ef8142da3))

- Update RDS metrics
  ([`3f8f561`](https://github.com/RedHatInsights/vmaas/commit/3f8f561c2ed94550ec54d3f7fa7f66d46a2397fe))


## v1.20.3 (2020-10-09)

### Bug Fixes

- **reposcan**: Detect case when sync process is killed and reposcan is stucked
  ([`b0797e8`](https://github.com/RedHatInsights/vmaas/commit/b0797e81b9d03cf54b647c02c4db188f7145006f))

### Chores

- Add python3-coverage to qe build
  ([`3809d9b`](https://github.com/RedHatInsights/vmaas/commit/3809d9b725a943673d68fe1e722c245d8f3ead14))

- Coverage binary name in ubi
  ([`ca89b60`](https://github.com/RedHatInsights/vmaas/commit/ca89b6070ffd8bb1557ffde298bd75eab3902573))

- Create new grafana dashboard and fix local container
  ([`fdc8339`](https://github.com/RedHatInsights/vmaas/commit/fdc833996eded7455541f39888e38dd96c84e26b))

- Integration tests openshift app entrypoint
  ([`9f49eab`](https://github.com/RedHatInsights/vmaas/commit/9f49eab11f143f52d84786e3b3fbf1af9a98cce7))

- Set to debug, it's overly verbose for some repos
  ([`4b351c5`](https://github.com/RedHatInsights/vmaas/commit/4b351c59981e49d6844a04e9d73147fc95ed608b))

- Use different uid for vmaas
  ([`5553385`](https://github.com/RedHatInsights/vmaas/commit/55533851c5d95045394b95961c2197f1b53b9d9a))


## v1.20.2 (2020-09-23)

### Bug Fixes

- **webapp**: Init logging once
  ([`dcbaff3`](https://github.com/RedHatInsights/vmaas/commit/dcbaff349b57c9b711c3a0b73130c39708e5fde8))

### Chores

- Improve logging settings
  ([`cdd6002`](https://github.com/RedHatInsights/vmaas/commit/cdd60025317d76e67c300690a6b48b10a8bc0090))


## v1.20.1 (2020-09-22)

### Bug Fixes

- **webapp**: Only format error if response has body
  ([`07c60d0`](https://github.com/RedHatInsights/vmaas/commit/07c60d09a7aed0f7409ace5b486909346b71ec67))


## v1.20.0 (2020-09-21)

### Bug Fixes

- Let pipenv see system site-packages
  ([`d5406ae`](https://github.com/RedHatInsights/vmaas/commit/d5406ae15def6b1194f3adca74563a2111dd14e3))

- Use new single app image
  ([`cb83321`](https://github.com/RedHatInsights/vmaas/commit/cb8332167b79f4accc87eed866b2a4ad74c4ad86))

- **common**: Updated tests for rpm.parser_rpm_name
  ([`9c505bf`](https://github.com/RedHatInsights/vmaas/commit/9c505bf2fd4bb0c49e1a575fb1f359ebf5d614dc))

- **reposcan**: Move function proper rpm module and reuse it
  ([`ba0124b`](https://github.com/RedHatInsights/vmaas/commit/ba0124b735bcd00446132694b4181792a24e0e7e))

- **webapp**: If there is no dump, websocket handler crashes due to KeyError
  ([`25ae1f5`](https://github.com/RedHatInsights/vmaas/commit/25ae1f55985ec32907c656ea5f6e9caf4518489f))

- **webapp**: Reuse function from common.rpm
  ([`9c3b2fa`](https://github.com/RedHatInsights/vmaas/commit/9c3b2faae773a379b191dd523dbc08abcad8cdb2))

### Features

- **webapp**: Added function to filter latest NEVRAs
  ([`f1a662c`](https://github.com/RedHatInsights/vmaas/commit/f1a662ce2215006c1b09e0c07c2d28cc846b897a))

- **webapp**: Install rpm module
  ([`675c4e6`](https://github.com/RedHatInsights/vmaas/commit/675c4e67c1786f7074b33a1ab33f22c4032b3553))

- **webapp**: Update /updates to support latest_only filtering
  ([`e1fe2af`](https://github.com/RedHatInsights/vmaas/commit/e1fe2afa441f2d857410c318ae91bfebb938b953))


## v1.19.2 (2020-09-14)

### Bug Fixes

- **webapp**: Expose readiness endpoint
  ([`878d2c4`](https://github.com/RedHatInsights/vmaas/commit/878d2c4b3d3a07a74534dddafa806cd7bd054eb3))


## v1.19.1 (2020-09-12)

### Bug Fixes

- Update developer mode to new single container
  ([`dd74dfa`](https://github.com/RedHatInsights/vmaas/commit/dd74dfab1e6b0f9a53661e4ccef05f07a1c6a90b))

- **webapp**: Don't block websocket during refresh
  ([`343044e`](https://github.com/RedHatInsights/vmaas/commit/343044ee957575ad62ad866a1e9ec59b3522813b))

- **websocket**: Progressively refresh webapps
  ([`7f79ed4`](https://github.com/RedHatInsights/vmaas/commit/7f79ed4fb930a188e1403eda80d370c40d48bd24))

Add readiness endpoint to webapp

Remove buffering queues from websocket implementations, make them steady-state

- **websocket**: Track ids of clients in log
  ([`1b169fc`](https://github.com/RedHatInsights/vmaas/commit/1b169fcdbe8afc259cbc44cb6eecfe9f3366e0ed))

### Chores

- Fix new pylint 2.6.0 issues
  ([`9500390`](https://github.com/RedHatInsights/vmaas/commit/9500390cdd9efac866ea217d18b0945a20e30163))

- Podman-compose from devel branch doesn't have stable checksum, drop it from dependencies
  ([`3ae38d8`](https://github.com/RedHatInsights/vmaas/commit/3ae38d8821e01b55a4cbc09a5047fac4049c6047))


## v1.19.0 (2020-09-02)

### Bug Fixes

- Build app image only once
  ([`a33dfdd`](https://github.com/RedHatInsights/vmaas/commit/a33dfddfde0da025cc4eb5d7427a13014e78e213))

### Chores

- Added deps for cloudwatch logging
  ([`edfc83b`](https://github.com/RedHatInsights/vmaas/commit/edfc83b2bb5a8a033612889c5816b7b74ab828fe))

### Features

- Added cloudwatch logging setup
  ([`2bf4c2d`](https://github.com/RedHatInsights/vmaas/commit/2bf4c2def3a29cd5304bb8698508fa6bec813ff6))


## v1.18.3 (2020-07-29)

### Bug Fixes

- **reposcan**: File content is required by crypto lib, not file name, also fixing detection for
  certs expiring in more than 30 days
  ([`11917f3`](https://github.com/RedHatInsights/vmaas/commit/11917f31e620f911f07be3745f882b716c93bca2))

- **reposcan**: Fixing ISE in prepare msg function
  ([`04c7258`](https://github.com/RedHatInsights/vmaas/commit/04c7258dfc630172ace90e73ad7ee8cfbe9c0104))

reposcan: [ERROR] Internal server error <-9223363273888645507>'Traceback (most recent call last):\n
  File "/vmaas/reposcan/repodata/repository_controller.py", line 81, in
  _check_cert_expiration_date\n loaded_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)\n
  File "/usr/local/lib/python3.6/site-packages/OpenSSL/crypto.py", line 1794, in load_certificate\n
  _raise_current_error()\n File "/usr/local/lib/python3.6/site-packages/OpenSSL/_util.py", line 54,
  in exception_from_error_queue\n raise exception_type(errors)\nOpenSSL.crypto.Error: [(\'PEM
  routines\', \'get_name\', \'no start line\')]\n\nDuring handling of the above exception, another
  exception occurred:\n\nTraceback (most recent call last):\n File "/vmaas/reposcan/reposcan.py",
  line 518, in run_task\n repository_controller.store()\n File
  "/vmaas/reposcan/repodata/repository_controller.py", line 272, in store\n failed =
  self._download_repomds()\n File "/vmaas/reposcan/repodata/repository_controller.py", line 72, in
  _download_repomds\n self._check_cert_expiration_date(cert_name, cert)\n File
  "/vmaas/reposcan/repodata/repository_controller.py", line 96, in _check_cert_expiration_date\n msg
  = prepare_msg_for_slack(cert_name, \'Reposcan CDN certificate not provided or incorrect\')\n File
  "/vmaas/reposcan/common/slack_notifications.py", line 48, in prepare_msg_for_slack\n (valid_to_dt,
  expire_in_days_td) = expire_tuple\nTypeError: \'NoneType\' object is not iterable'|

### Chores

- Update vmaas qe build on openshift
  ([`d1eac98`](https://github.com/RedHatInsights/vmaas/commit/d1eac98c2f0f596eedd6e7ecf80e57e4f2082188))


## v1.18.2 (2020-07-23)

### Bug Fixes

- Fix path to wait script
  ([`d0fcdc1`](https://github.com/RedHatInsights/vmaas/commit/d0fcdc103970cdcdda68e781bc902fa4541209ce))

### Documentation

- Specify possible values in schema
  ([`75a6de7`](https://github.com/RedHatInsights/vmaas/commit/75a6de7575b37f345ab2517343535ee56cf33060))

Removed basearch enum

Removed commented code

Finished updating specs.

Moved null to end

### Refactoring

- Use single dockerfile for all app services
  ([`aa21829`](https://github.com/RedHatInsights/vmaas/commit/aa21829807ced2b2339834972e2dd52f92a19497))


## v1.18.1 (2020-07-10)

### Bug Fixes

- **reposcan**: Export pkg_cve mappings only for cves with source
  ([`3bb9bac`](https://github.com/RedHatInsights/vmaas/commit/3bb9bacc56b6502f6f11aa5e88f1bba11ed5f564))


## v1.18.0 (2020-07-09)

### Features

- **reposcan**: Add cdn expiration notifications to slack
  ([`25e61f4`](https://github.com/RedHatInsights/vmaas/commit/25e61f400538b5f4ead453af74422ae82c658b51))


## v1.17.4 (2020-07-08)

### Bug Fixes

- **websocket**: Fix key error and incorrect timestamp extraction
  ([`3c0e4c0`](https://github.com/RedHatInsights/vmaas/commit/3c0e4c0815deaff3fa0c359fd88878dab54b56f7))


## v1.17.3 (2020-07-02)

### Bug Fixes

- **webapp**: Added non module testing update into the webapp tests
  ([`3041854`](https://github.com/RedHatInsights/vmaas/commit/30418541e9f403a6d5028534cf8a35ac2b28f95b))

- **webapp**: Removed updates when modules_list is not provided
  ([`952a89c`](https://github.com/RedHatInsights/vmaas/commit/952a89cdaa5a907cd753bbe009aefa26fe64b22e))

- **webapp**: Updated tests default modules update
  ([`ad063ef`](https://github.com/RedHatInsights/vmaas/commit/ad063ef46647596ef6e9936ea9d8e28cc356e3cd))


## v1.17.2 (2020-06-25)

### Bug Fixes

- **webapp**: Fixed webapp response gzipping
  ([`29d7988`](https://github.com/RedHatInsights/vmaas/commit/29d798845dc0bfcdb1898cdd6dc4d43f85b13644))


## v1.17.1 (2020-06-24)

### Bug Fixes

- **reposcan**: Add src_pkg_names to content set mapping to cache
  ([`c7020e7`](https://github.com/RedHatInsights/vmaas/commit/c7020e701616a2adcef033bc5a5cb6f1b39803de))

- **reposcan**: Delete rows from module_rpm_artifact
  ([`f8889a4`](https://github.com/RedHatInsights/vmaas/commit/f8889a4fc3449bdc29187518e0d500f83948f8c0))


## v1.17.0 (2020-06-19)

### Bug Fixes

- **reposcan**: Fix bugs in db tests
  ([`4156bfb`](https://github.com/RedHatInsights/vmaas/commit/4156bfbcceea1b12d7756aa76413e3556905c0ed))

### Features

- **webapp**: Unify errata severity none to null
  ([`f2cddad`](https://github.com/RedHatInsights/vmaas/commit/f2cddad847ffdd6a9577a295945cb4f058cfc232))


## v1.16.1 (2020-06-16)

### Bug Fixes

- **reposcan**: Close DB connection when background tasks finishes
  ([`4d0d3a8`](https://github.com/RedHatInsights/vmaas/commit/4d0d3a84903f5eb91119443cfe066249b7a20a19))

### Refactoring

- Tag experimental endpoints
  ([`51b97fa`](https://github.com/RedHatInsights/vmaas/commit/51b97fab0b3d13f085b1a80e098b7e12ca341fbf))


## v1.16.0 (2020-06-11)

### Features

- **webapp**: Return only those CVEs which have errata associated
  ([`c602508`](https://github.com/RedHatInsights/vmaas/commit/c602508179ec9083a86718d3c5e3379cbc1e05ff))

### Refactoring

- Remove version lock workaround
  ([`75f702b`](https://github.com/RedHatInsights/vmaas/commit/75f702bf9a83f440ed60ccbecd33c9eb8ca47179))


## v1.15.2 (2020-06-05)

### Bug Fixes

- **webapp**: Removed redundant product check
  ([`1a8a5ba`](https://github.com/RedHatInsights/vmaas/commit/1a8a5ba355ab314143653a7d8e8eb421c3de7a59))

including updates from different repos of the same product confuses users because they see updates
  from repos which they do not have enabled

### Refactoring

- **database**: Initialize schema if database container is not present (RDS)
  ([`9be7e4c`](https://github.com/RedHatInsights/vmaas/commit/9be7e4cd3b3d0ce22599851800385951a2735062))

### Testing

- Install gcc, python3-devel due to psutil build and remove ubi8 version lock
  ([`664cf1f`](https://github.com/RedHatInsights/vmaas/commit/664cf1ffd68317f399ee96b18c3d7d958a9c6eef))


## v1.15.1 (2020-05-26)

### Bug Fixes

- **webapp**: Fixed gzip middleware null-pointer
  ([`134fcf8`](https://github.com/RedHatInsights/vmaas/commit/134fcf8da5ed598701416ceb59b6ebd5f41ad5d8))


## v1.15.0 (2020-05-22)

### Features

- **common**: Add slack notification module
  ([`3664752`](https://github.com/RedHatInsights/vmaas/commit/3664752de9429d7e2c9f0c0d2aaef8b830f06014))


## v1.14.1 (2020-05-20)

### Bug Fixes

- **reposcan**: Export package names without errata
  ([`05fe569`](https://github.com/RedHatInsights/vmaas/commit/05fe569a6377a6a0defbc17f81f45217b85cefb0))

### Testing

- Make upgrade test work in dirty git in container
  ([`5acb7ec`](https://github.com/RedHatInsights/vmaas/commit/5acb7ec67cfbbf51b503ef58ef1f93386856ace6))


## v1.14.0 (2020-05-18)

### Chores

- Pipenv check workaround
  ([`5c6ac7d`](https://github.com/RedHatInsights/vmaas/commit/5c6ac7d613c05355d1d4f4f3c5af6d8a9891dce2))

https://github.com/pypa/pipenv/issues/4188

PIPENV_PYUP_API_KEY= can be removed when pipenv-2020.X.X is released

### Features

- **webapp**: Add errata filtering by severity and errata type
  ([`b0b4df5`](https://github.com/RedHatInsights/vmaas/commit/b0b4df5308779551a9b3abd83e44e81b18972279))


## v1.13.5 (2020-05-05)

### Bug Fixes

- **webapp**: Fix content set filtering in package_names/srpms api endpoint
  ([`ee323bf`](https://github.com/RedHatInsights/vmaas/commit/ee323bfc0da8ad80efffe8c936d80f488f862214))


## v1.13.4 (2020-05-05)

### Bug Fixes

- **webapp**: Remove unused argument and imports
  ([`5a695d7`](https://github.com/RedHatInsights/vmaas/commit/5a695d72561f1899c1538caae50efc2246bfd6eb))

- **webapp**: Removed hotcache
  ([`68e7528`](https://github.com/RedHatInsights/vmaas/commit/68e75287205d5107a6393d7995e56f872ad40dbc))

according to performance testing and the production monitoring the hit/miss ratio of the hotcache is
  so low that it's actually slowing evaluation

### Chores

- Deploy to openshift
  ([`360cf5e`](https://github.com/RedHatInsights/vmaas/commit/360cf5ef3501503beb805daa1d95613493c27fe2))

- Fix collecting openshift logs in actions
  ([`b32c0da`](https://github.com/RedHatInsights/vmaas/commit/b32c0da151f9f58b5d0430524d0d111dfcb03ded))

- Re-lock dependencies to update pylint
  ([`6226541`](https://github.com/RedHatInsights/vmaas/commit/6226541e10a65fd145acdf3e0c2c0e7958f309fd))

Pylint 2.5.0 no longer allows python -m pylint ... to import user code. Previously, it added the
  current working directory as the first element of sys.path. This opened up a potential security
  hole where pylint would import user level code as long as that code resided in modules having the
  same name as stdlib or pylint's own modules.

### Testing

- Fix pylint 2.5.0 issues
  ([`f90dcb6`](https://github.com/RedHatInsights/vmaas/commit/f90dcb660864fed852436e16a7b90c46794a7e2e))


## v1.13.3 (2020-04-27)

### Bug Fixes

- **webapp**: Distinguish existining and nonex. packages on /rpms
  ([`e417401`](https://github.com/RedHatInsights/vmaas/commit/e4174019434d0b00a2d6c8be30c80771ae8c2036))

- **webapp**: Distinguish existining and nonex. packages on /srpms
  ([`d7f4e50`](https://github.com/RedHatInsights/vmaas/commit/d7f4e500a320cc6916c196ed4bd9b88097b82f40))

### Chores

- Fix upgrade test to find old commit
  ([`d1a217b`](https://github.com/RedHatInsights/vmaas/commit/d1a217b710b51202ad5bbc3dee6e45593b07cc97))


## v1.13.2 (2020-04-22)

### Bug Fixes

- **reposcan**: Do not show bad token to log
  ([`c4f1c0d`](https://github.com/RedHatInsights/vmaas/commit/c4f1c0d36556860ffd40250f18a1f3cc7db1208a))


## v1.13.1 (2020-04-20)

### Bug Fixes

- Patches API should return ALL errata, not just security ones
  ([`82f80a8`](https://github.com/RedHatInsights/vmaas/commit/82f80a87c136791643ef6285e900bc2455bb3fc4))


## v1.13.0 (2020-04-20)

### Features

- **webapp**: Add /package_names api endpoint
  ([`bda5cb5`](https://github.com/RedHatInsights/vmaas/commit/bda5cb5ef880b7a697c67ccf6d56870f2d64f9ca))

test(package_names): add unit tests for package_names

feat(webapp): move from /package_names to /package_names/srpms and separate srpms and rpms calls and
  add GET method to /srpms

- **webapp**: Add new POST and GET /package_names/rpms API endpoint
  ([`a64aa2e`](https://github.com/RedHatInsights/vmaas/commit/a64aa2e8b5b6fcb63a815387baec1724571cfa15))


## v1.12.2 (2020-04-17)

### Bug Fixes

- There may not be any dump loaded
  ([`4fbb326`](https://github.com/RedHatInsights/vmaas/commit/4fbb3268f7ccc5077281b093dd5303e7c983fde0))

- **database**: Default 64mb is not always enough for PostgreSQL 12
  ([`0677cab`](https://github.com/RedHatInsights/vmaas/commit/0677cab792eec7e4928251055f96ebcf04616ee4))

### Chores

- Disable PIPENV_CHECK in actions run
  ([`6bcccf9`](https://github.com/RedHatInsights/vmaas/commit/6bcccf952542bf0a60573fcdba7e2e28f113dee1))

- Fix command in devel docker composes for podman-compose
  ([`2d10aef`](https://github.com/RedHatInsights/vmaas/commit/2d10aefca114359b142b751202ad5fc86617a7ed))

- Run actions only on pushes to master+stable and on PRs to stable (coming from branch on same repo
  to make it work)
  ([`336f062`](https://github.com/RedHatInsights/vmaas/commit/336f06268487ef2ae29ef1a92e7dd7a30551609f))


## v1.12.1 (2020-04-16)

### Bug Fixes

- **webapp**: Don't block API during cache refreshes
  ([`9b85909`](https://github.com/RedHatInsights/vmaas/commit/9b8590991853d94f4b40e75967624f6a861ced01))

- **webapp**: Switch to refreshing mode and return 503
  ([`f5e15ab`](https://github.com/RedHatInsights/vmaas/commit/f5e15ab4a52f81d1b4d4ef3510c7d7773d7f1516))

### Chores

- Allow to get PIPENV_CHECK variable from host environment
  ([`89c0e08`](https://github.com/RedHatInsights/vmaas/commit/89c0e08fdccb68f4c2bfe13a8b8294dc1366e84d))

allows commands like: $ PIPENV_CHECK=0 docker-compose up --build


## v1.12.0 (2020-04-15)

### Chores

- Fix missing /common in developer setup
  ([`670040a`](https://github.com/RedHatInsights/vmaas/commit/670040aae51da85358b2fceea3ac651eb8c533a0))

- Fix podman devel setup
  ([`665bf0b`](https://github.com/RedHatInsights/vmaas/commit/665bf0b2bf17c1b7c8c12b4bc25fffef9ec2c1dd))

- Make an easy way to disable pipenv check when necessary
  ([`24f269b`](https://github.com/RedHatInsights/vmaas/commit/24f269b862d42edfef4b849488e1a37902987c55))

- Pass PIPENV_CHECK variable to test build from travis env
  ([`1711814`](https://github.com/RedHatInsights/vmaas/commit/1711814bb6630d16182bd08015252cd9ea315d22))

### Features

- **webapp**: New API to list only applicable errata to a package list
  ([`8c92679`](https://github.com/RedHatInsights/vmaas/commit/8c9267983ccc1f6a61a7575b4148be6f8a159dfe))


## v1.11.3 (2020-04-09)

### Bug Fixes

- **reposcan**: 8.1-409 has broken dependencies in UBI repo
  ([`edfee79`](https://github.com/RedHatInsights/vmaas/commit/edfee7945f61d40565ea1dcf9504c38f4e3508bd))

error: Error running transaction: package systemd-libs-239-18.el8_1.5.x86_64 (which is newer than
  systemd-libs-239-18.el8_1.4.x86_64) is already installed

### Chores

- Remove obsoleted deployment scripts
  ([`89b390e`](https://github.com/RedHatInsights/vmaas/commit/89b390e27a540574808ac17d25414f048f9c364f))

- Use secrets project for vmaas secrets in jenkins
  ([`77e9fbd`](https://github.com/RedHatInsights/vmaas/commit/77e9fbd855fd2a42ebe6d4d8f22a9c5a8cdf9359))


## v1.11.2 (2020-03-31)

### Bug Fixes

- **webapp**: Add webapp automatical reconnect to ws
  ([`403e209`](https://github.com/RedHatInsights/vmaas/commit/403e209ff5a9d7dcd7d58ce1a005c1dab2a9d902))

- **webapp**: Fix cache data race fetching when websocket crashes
  ([`d9c9ae8`](https://github.com/RedHatInsights/vmaas/commit/d9c9ae8acee1ada883e3cb4e7dc0cc3c5a1d28e5))


## v1.11.1 (2020-03-27)

### Bug Fixes

- 'pipenv install' re-generates lockfile by default, install only from what's already in lockfile
  ([`3fde6d4`](https://github.com/RedHatInsights/vmaas/commit/3fde6d4fc8a1a4008f9bb4914f007cbfdc0cc772))

- Update pyyaml (CVE-2020-1747) and some others to fix tests
  ([`24a6890`](https://github.com/RedHatInsights/vmaas/commit/24a68904f23ada927bc1687aff11630bc664d5e9))

- **reposcan**: Duplicate error when import repos
  ([`29d275e`](https://github.com/RedHatInsights/vmaas/commit/29d275e96b6cc684c048112dfa7e8bff86c4efd7))

- **reposcan**: Pg 12 to_timestamp() behaviour changed
  ([`1a05925`](https://github.com/RedHatInsights/vmaas/commit/1a05925f032c48323f0be3b5b2a1e82838b89350))

PG 10: select to_timestamp('2020-03-26 19:38:26.195650+00:00', 'YYYY-MM-DD HH24:MI:SS.US'); PASS
  select to_timestamp('2020-03-26T19:37:00.846691+00:00', 'YYYY-MM-DD HH24:MI:SS.US'); PASS

but PG 12: select to_timestamp('2020-03-26 19:38:26.195650+00:00', 'YYYY-MM-DD HH24:MI:SS.US'); PASS
  select to_timestamp('2020-03-26T19:37:00.846691+00:00', 'YYYY-MM-DD HH24:MI:SS.US'); FAIL

this works: select to_timestamp('2020-03-26 19:38:26.195650+00:00', 'YYYY-MM-DDTHH24:MI:SS.US');
  PASS select to_timestamp('2020-03-26T19:37:00.846691+00:00', 'YYYY-MM-DDTHH24:MI:SS.US'); PASS

### Testing

- Base test image on UBI 8 and PG 12
  ([`43d9985`](https://github.com/RedHatInsights/vmaas/commit/43d99854d44b78e7006f93abf3dad59a4d2440ad))

- Workaround using UnsafeLoader in tests
  ([`8ed26bd`](https://github.com/RedHatInsights/vmaas/commit/8ed26bdb9c927f9e6750a644b7e133d5511ee453))


## v1.11.0 (2020-03-25)

### Bug Fixes

- **reposcan**: Install postgresql for DB migrations
  ([`e8b6210`](https://github.com/RedHatInsights/vmaas/commit/e8b621092b5ffd2e282ebc44c25c29e4fc6fbf19))

- not available from UBI repos - microdnf install from custom repo fails in OpenShift env, using
  workaround using rpm

### Features

- **database**: Upgrade to PostgreSQL 12
  ([`b6c61a9`](https://github.com/RedHatInsights/vmaas/commit/b6c61a9b25075135f0f7a461c5c3b8c3dee9b904))

re-introduce 2 dockerfiles because registry.redhat.io doesn't allow unauthenticated download


## v1.10.3 (2020-03-24)

### Bug Fixes

- **reposcan**: Set source id to null instead of deleting it
  ([`613c615`](https://github.com/RedHatInsights/vmaas/commit/613c6150fdb0ecff2dc535f74ffa718728ac4624))


## v1.10.2 (2020-03-23)

### Bug Fixes

- **reposcan**: Invalidate webapp cache only when task succeeded
  ([#678](https://github.com/RedHatInsights/vmaas/pull/678),
  [`c9befc5`](https://github.com/RedHatInsights/vmaas/commit/c9befc5cc97bbebc9fddddab116f096e4e1775d4))


## v1.10.1 (2020-03-18)

### Bug Fixes

- Check on system level to find vulnerabilities and workaround pipenv to make it work
  ([`6c5f6db`](https://github.com/RedHatInsights/vmaas/commit/6c5f6dbab5e21c20ea1bbac6d61c587f0776f1b2))

- Revert "temporarily ignore cve in pipenv"
  ([`20e535b`](https://github.com/RedHatInsights/vmaas/commit/20e535b37f7f3c4161b941952b372274b2da0fea))

This reverts commit ec23cb5226ded5d245c3bfce244f190481ad676c.


## v1.10.0 (2020-03-18)

### Chores

- Add database upgrades unit tests
  ([`0b698f7`](https://github.com/RedHatInsights/vmaas/commit/0b698f7302d1c678a71b2b39aeb395d437bc217a))

### Features

- **database**: Add database upgrade scripts and tutorial
  ([`d5ce37e`](https://github.com/RedHatInsights/vmaas/commit/d5ce37e4b9ae8fd93adab80946ede0e36f5a5565))

### Testing

- Replace commit ref with actual one
  ([`5645482`](https://github.com/RedHatInsights/vmaas/commit/56454821420688d081063343b98ea6287aeb44f4))


## v1.9.0 (2020-03-12)

### Chores

- **reposcan**: Add pyOpenSSL library
  ([`e98f563`](https://github.com/RedHatInsights/vmaas/commit/e98f5634835a5a213f2dfb460aac0df622bb5dcf))

### Features

- **reposcan**: Add function to check cert expiration date
  ([`857fe35`](https://github.com/RedHatInsights/vmaas/commit/857fe350fa95e1bfe10b9d946b3cde92bd8faee9))


## v1.8.0 (2020-03-11)

### Features

- **webapp**: Add autoscaler to webapp, format secrets as a list of yaml values
  ([`58d7a56`](https://github.com/RedHatInsights/vmaas/commit/58d7a5697874d481163b59c120035b4e2add754b))


## v1.7.0 (2020-03-10)

### Features

- **webapp**: Add lite error formatter
  ([`98bacd3`](https://github.com/RedHatInsights/vmaas/commit/98bacd3b0be1e76676bf6ad3a222e50dbf6902b1))


## v1.6.1 (2020-03-09)

### Bug Fixes

- Temporarily ignore cve in pipenv
  ([`ec23cb5`](https://github.com/RedHatInsights/vmaas/commit/ec23cb5226ded5d245c3bfce244f190481ad676c))

### Chores

- Remove error formatter
  ([`abe093b`](https://github.com/RedHatInsights/vmaas/commit/abe093b4faab86c948c1e1895db81214928b4f1c))

- Upgrade connexion version
  ([`f6c7d3b`](https://github.com/RedHatInsights/vmaas/commit/f6c7d3bd96cf8cce61272ef8c8dc67e7d873bd43))


## v1.6.0 (2020-03-05)

### Features

- **reposcan**: Add failed repo-download methrics for different http codes
  ([`80b71a8`](https://github.com/RedHatInsights/vmaas/commit/80b71a85b758df39e37d9ddaec611c89b67eb39a))


## v1.5.0 (2020-02-26)

### Chores

- Jenkinsfile line continuation
  ([`e4b16bb`](https://github.com/RedHatInsights/vmaas/commit/e4b16bbbc79cf9e56a5138673b6fdd9e52d08dfc))

- Run Actions on PR to master/stable, Jenkins against master/stable
  ([`1017f73`](https://github.com/RedHatInsights/vmaas/commit/1017f73958f5910219f46d951b6469c7af3d4c42))

### Features

- Add pkgtree API endpoint to webapp ([#650](https://github.com/RedHatInsights/vmaas/pull/650),
  [`b56c681`](https://github.com/RedHatInsights/vmaas/commit/b56c681916919e85d690125e756c2a783a7195df))

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

* webapp pkgtree - first tests pass

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

* Revert back webapp yaml cache to full_load


## v1.4.4 (2020-02-18)

### Bug Fixes

- **reposcan**: Use left join instead of inner
  ([`1288da4`](https://github.com/RedHatInsights/vmaas/commit/1288da4d29f2de511353786021085e21db810037))

### Chores

- Delete correct pvc
  ([`3b79649`](https://github.com/RedHatInsights/vmaas/commit/3b796491d422bffa1d7bf30e7dd64862fdf90afb))


## v1.4.3 (2020-02-18)

### Bug Fixes

- **webapp**: Set 415 error code and change detail message for incorrect content type
  ([`bd37916`](https://github.com/RedHatInsights/vmaas/commit/bd37916779c55555d63d21c7f47d6d5457a664e5))

### Chores

- Run jenkins only on master branch
  ([`503c9dd`](https://github.com/RedHatInsights/vmaas/commit/503c9dddc0e4f44eb77ef1179bb9bc9cb276a50a))

- Use github actions for integration tests
  ([`9087c97`](https://github.com/RedHatInsights/vmaas/commit/9087c97eea08d63d1b86e6f59f4c6d4fa77ef965))

- Workaround ocdeployer bug
  ([`54b3e24`](https://github.com/RedHatInsights/vmaas/commit/54b3e24cf0a7b78c853987aa680c595b1d3c0327))


## v1.4.2 (2020-02-18)

### Bug Fixes

- **database**: Store null severity in errata table
  ([`0657527`](https://github.com/RedHatInsights/vmaas/commit/065752791726a28f7f934b3b409ca2a03e6009fa))

fix(reposcan): import null severity to db

fix(webapp): return null instead of empty string


## v1.4.1 (2020-01-28)

### Bug Fixes

- **reposcan**: Init logging in Git sync
  ([`c10fff8`](https://github.com/RedHatInsights/vmaas/commit/c10fff83c7f03c8c0d1fbc976d7d95327d6a8b3d))

- **reposcan**: Repo is empty string because stdout of git clone is empty
  ([`91a7e75`](https://github.com/RedHatInsights/vmaas/commit/91a7e75ab6b297282ca9dc0cbfa9b44cd420bdca))

remove assert and rely only on validation below that repo file has been downloaded

related probably to switch to UBI 8 images and newer git version


## v1.4.0 (2020-01-27)

### Features

- **reposcan**: Add metrics to count failed imports of cves and repos
  ([`e17de4d`](https://github.com/RedHatInsights/vmaas/commit/e17de4d5848195593d9b5c6eda7e1db7db978c67))


## v1.3.6 (2020-01-14)

### Bug Fixes

- **manifests**: Fix manifest push process
  ([`c48d226`](https://github.com/RedHatInsights/vmaas/commit/c48d2268f868760d4be24e6b96d76e130f7a1036))

### Chores

- Ignore coverage of python modules in /usr
  ([`3db0299`](https://github.com/RedHatInsights/vmaas/commit/3db0299ddf906e586ad0797acc3115738d78b254))


## v1.3.5 (2020-01-10)

### Bug Fixes

- Obsolete Dockerfile diff test
  ([`9167f22`](https://github.com/RedHatInsights/vmaas/commit/9167f228ac30b6e2a80df1a3df10ba5582204acb))

- Obsolete suffixes in OpenShift deployment
  ([`a9f21fd`](https://github.com/RedHatInsights/vmaas/commit/a9f21fdb69bcd8064f01a05ab951c065420e2523))

- **reposcan**: Xml tree evaluates found elements as False
  ([`8e7b24e`](https://github.com/RedHatInsights/vmaas/commit/8e7b24edfe3ef172cce709e744c2d067f1ef538b))

### Chores

- Migrate CentOS 7 images to RHEL 8 UBI and obsolete RHEL 7
  ([`343365a`](https://github.com/RedHatInsights/vmaas/commit/343365af8c2dd97d3599b409576416874a9aec1b))

- Remove obsoleted Dockerfile
  ([`b924e38`](https://github.com/RedHatInsights/vmaas/commit/b924e380e51d9ec86b8daac904770a0ab64ac882))

- Remove obsoleted script
  ([`f4a6459`](https://github.com/RedHatInsights/vmaas/commit/f4a64593a5e5a552b6bf5cf60b6736f347f9f334))

- Use only RHEL-based Dockerfile
  ([`5acc5db`](https://github.com/RedHatInsights/vmaas/commit/5acc5db9f6e866395269556e99b094a7287426a7))

### Refactoring

- Wait for postgresql without psql
  ([`510dd5a`](https://github.com/RedHatInsights/vmaas/commit/510dd5a46b2bd9dc1b18e3e514f299182534814d))


## v1.3.4 (2020-01-08)

### Bug Fixes

- **reposcan**: Duplicate conflict while importing repos
  ([`ffd4b00`](https://github.com/RedHatInsights/vmaas/commit/ffd4b00a9e81a79e3b432bc3ee1008df3d9dfd16))


## v1.3.3 (2019-12-18)

### Bug Fixes

- **reposcan**: Syntax error while deleting repos
  ([`a58e48c`](https://github.com/RedHatInsights/vmaas/commit/a58e48c185b0378d67d5ce4993c593444da88c4a))


## v1.3.2 (2019-12-10)

### Bug Fixes

- **reposcan**: Delete module by repo fk reference
  ([`d192ff1`](https://github.com/RedHatInsights/vmaas/commit/d192ff1b4667c8cbc60f7f59c6e4cae07c8e2ede))


## v1.3.1 (2019-12-09)

### Bug Fixes

- **webapp**: Fix 500 error when empty modules_list
  ([`caa6edf`](https://github.com/RedHatInsights/vmaas/commit/caa6edf198ae5b87af1b8b89519c6113c17d8b08))

### Chores

- Fix reposcan:/data ownership in devel setup
  ([`3e42d9e`](https://github.com/RedHatInsights/vmaas/commit/3e42d9e94faba33bfccd57200820687f51835c48))

- Jenkinsfile path to tests
  ([`df782e1`](https://github.com/RedHatInsights/vmaas/commit/df782e163aacf7ecafb7ea25a49cdf89fb1175cb))

Without slash it runs also vulnerability tests because of jenkins workspace path @jdobes was too
  fast and merged it before my force push :smile:

- Update vmaas tests path
  ([`4dba197`](https://github.com/RedHatInsights/vmaas/commit/4dba197f018ccdff41c7d78c7febc345bab0e8bb))

### Refactoring

- **websocket**: Unify entrypoint in websocket with other containers
  ([`6e6c8a0`](https://github.com/RedHatInsights/vmaas/commit/6e6c8a0b8597e90a097b8807ff70d5d8a17712c4))


## v1.3.0 (2019-12-03)

### Features

- **reposcan**: Export all updates, not only security
  ([`2373c48`](https://github.com/RedHatInsights/vmaas/commit/2373c484d956235d4341e736c9110a84c867ba89))

- **webapp**: Add new version of /updates API
  ([`3566ff2`](https://github.com/RedHatInsights/vmaas/commit/3566ff2088c875d55891c38fb8cfad654bd15d4b))

allowing to return all/security updates only based on 'security_only' parameter


## v1.2.1 (2019-11-27)

### Bug Fixes

- **reposcan**: Optimize and fix source package associations
  ([`9d41a50`](https://github.com/RedHatInsights/vmaas/commit/9d41a50163916e2e19330a0ff00f3d9f1983257c))


## v1.2.0 (2019-11-26)

### Bug Fixes

- **reposcan**: Create always pre-defined redhat_url
  ([`fd2efe8`](https://github.com/RedHatInsights/vmaas/commit/fd2efe8301a1f562097028b3906843317b6d8968))

- **reposcan**: Store references from cvemap as secondary url
  ([`8934aac`](https://github.com/RedHatInsights/vmaas/commit/8934aac47431d16507fd96f1d25cadf59999cb8e))

- **reposcan**: Sync IAVA when available
  ([`1768ad7`](https://github.com/RedHatInsights/vmaas/commit/1768ad7b8e66a00cff0783961fe42bea4cbbd7ab))

### Features

- **reposcan**: Don't sync CVEs from NIST
  ([`8d88702`](https://github.com/RedHatInsights/vmaas/commit/8d887020ca6fa00ffa52dfcf923633d4b043b860))


## v1.1.5 (2019-11-26)

### Bug Fixes

- **reposcan**: Pkgtree is exported and not synced, fix endpoints
  ([`f762c46`](https://github.com/RedHatInsights/vmaas/commit/f762c46d0efea3b4795d3342bd03477ade2454b1))


## v1.1.4 (2019-11-21)

### Bug Fixes

- **webapp**: Fix sending message to websocket
  ([`aa54f0b`](https://github.com/RedHatInsights/vmaas/commit/aa54f0b35f4cb62a26b94d62403c00efc88ecc3e))

### Refactoring

- **websocket**: Add logging
  ([`ec40163`](https://github.com/RedHatInsights/vmaas/commit/ec40163239cfb0c255abcebfdbfbfed0d9b87e10))


## v1.1.3 (2019-11-21)

### Bug Fixes

- **reposcan**: Revision has to be updated but only sometimes
  ([`66a4e43`](https://github.com/RedHatInsights/vmaas/commit/66a4e4394b621149473ea905325de464b281d977))

### Chores

- **travis**: Run on stable branch to generate doc
  ([`7f8841b`](https://github.com/RedHatInsights/vmaas/commit/7f8841bd21b7c2632540879617f7b462305459b0))


## v1.1.2 (2019-11-20)

### Bug Fixes

- Correctly display version in swagger
  ([`c88f0d1`](https://github.com/RedHatInsights/vmaas/commit/c88f0d14621b8d1f1b1c05494bb970bcbfba3211))


## v1.1.1 (2019-11-20)

### Bug Fixes

- **reposcan**: Don't reset timestamp and update only things that make sense
  ([`153371b`](https://github.com/RedHatInsights/vmaas/commit/153371b084db186b84959cdee0ebc1565c705e17))


## v1.1.0 (2019-11-19)

### Bug Fixes

- **reposcan**: Add missing default CDN cert variables
  ([`4cdd962`](https://github.com/RedHatInsights/vmaas/commit/4cdd962094fbae813d22b1e6682709012660c87f))

- **reposcan**: Change endpoint to more appropriate
  ([`cfb7672`](https://github.com/RedHatInsights/vmaas/commit/cfb7672cd114b4d76f6a6c420cab118e1965d66f))

- **reposcan**: Don't flood logs with error when there is lot of errors
  ([`62fb346`](https://github.com/RedHatInsights/vmaas/commit/62fb34655e027e0faad88bfc248240f6a22646ec))

interrupt download instead

- **reposcan**: Don't run export when new (empty) repos are added
  ([`75d027a`](https://github.com/RedHatInsights/vmaas/commit/75d027acf8e345a50dada03ed9b709f8085d65cf))

- **reposcan**: Fix github access from openshift
  ([`7949e82`](https://github.com/RedHatInsights/vmaas/commit/7949e82ffae71dc5a12c7f8c6da29559236072c9))

- **reposcan**: Run git download in periodic sync
  ([`4d732da`](https://github.com/RedHatInsights/vmaas/commit/4d732da49bd5afc5b84afe8dc23d3036e3f44235))

### Chores

- Lock different container due to pipeline-lib-v3
  ([`27a1ded`](https://github.com/RedHatInsights/vmaas/commit/27a1dedb071f46842e686dc21bcb6483de070030))

### Features

- **reposcan**: Add an api call to load repositories from git
  ([`92bf0ff`](https://github.com/RedHatInsights/vmaas/commit/92bf0ff056eae701edc56f408c35f80dc6925f68))


## v1.0.0 (2019-11-15)


## v0.13.0 (2019-06-12)


## v0.12.0 (2019-04-23)


## v0.11.0 (2019-04-02)


## v0.10.0 (2019-02-21)


## v0.9.0 (2018-12-19)


## v0.8.0 (2018-10-17)


## v0.7.0 (2018-09-17)


## v0.6.0 (2018-08-01)


## v0.5.0 (2018-06-20)


## v0.4.0 (2018-05-17)


## v0.3.0 (2018-04-06)


## v0.2.0 (2018-03-15)


## v0.1.0 (2018-03-08)
