# vmaas-go
Load VMaaS sqlite dump and access it via simple web server.

## Build
~~~bash
go build -o vmaas-go main.go
~~~

## Usage
Load dump and start simple server.
~~~bash
./vmaas-go ./path/too/vmaas-dump.db
~~~

Inspect data via web interface.
~~~bash
curl -v http://localhost:8080/ErrataDetail | python -m json.tool
~~~
Available endpoints = `Cache` object fileds:
- Packagename2Id
- Id2Packagename
- Updates
- UpdatesIndex
- Evr2Id
- Id2Evr
- Id2Arch
- Arch2Id
- ArchCompat
- PackageDetails
- Nevra2PkgId
- RepoDetails
- RepoLabel2Ids
- ProductId2RepoIds
- PkgId2RepoIds
- ErrataId2Name
- PkgId2ErrataIds
- ErrataId2RepoIds
- CveDetail
- PkgErrata2Module
- ModuleName2Ids
- DbChange
- ErrataDetail
- SrcPkgId2PkgId
- String
