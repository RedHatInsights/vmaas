package cache

import (
	"database/sql"
	"time"
)

type RepoID int
type PkgID int
type NameID int
type EvrID int
type ArchID int
type ErrataID int

type Cache struct {
	Packagename2Id map[string]NameID
	Id2Packagename map[NameID]string

	// name -> []pkg ordered by e-v-r ordering
	Updates map[NameID][]PkgID
	// name -> evr -> idx into updates[name]
	UpdatesIndex map[NameID]map[EvrID][]int

	Evr2Id map[Evr]EvrID
	Id2Evr map[EvrID]Evr

	Id2Arch map[ArchID]string
	Arch2Id map[string]ArchID

	ArchCompat map[ArchID]map[ArchID]bool

	PackageDetails map[PkgID]PackageDetail
	Nevra2PkgId    map[Nevra]PkgID

	RepoDetails   map[RepoID]RepoDetail
	RepoLabel2Ids map[string][]RepoID

	ProductId2RepoIds map[int][]RepoID
	PkgId2RepoIds     map[PkgID][]RepoID

	ErrataId2Name    map[ErrataID]string
	PkgId2ErrataIds  map[PkgID][]ErrataID
	ErrataId2RepoIds map[ErrataID][]RepoID

	CveDetail map[string]CveDetail
	CveNames  map[int]string

	PkgErrata2Module map[PkgErrata][]int
	ModuleName2Ids   map[ModuleStream][]int
	DbChange         DbChange
	ErrataDetail     map[string]ErrataDetail
	SrcPkgId2PkgId   map[PkgID][]PkgID
	String           map[int]string
}

type PackageDetail struct {
	NameId        NameID
	EvrId         EvrID
	ArchId        ArchID
	SummaryId     int
	DescriptionId int

	SrcPkgId *PkgID
}

type Evr struct {
	Epoch   int
	Version string
	Release string
}

type Nevra struct {
	NameId NameID
	EvrId  EvrID
	ArchId ArchID
}

type RepoDetail struct {
	Label      string
	Name       string
	Url        string
	BaseArch   *string
	ReleaseVer *string
	Product    string
	ProductId  int
	Revision   string
}

type CveDetail struct {
	RedHatUrl     *string
	SecondaryUrl  *string
	Cvss3Score    *float64
	Cvss3Metrics  *string
	Impact        string
	PublishedDate *time.Time
	ModifiedDate  *time.Time
	Iava          *string
	Description   string
	Cvss2Score    *float64
	Cvss2Metrics  *string
	Source        string

	CWEs      []string
	PkgIds    []int
	ErrataIds []int
}

type PkgErrata struct {
	PkgId    int
	ErrataId int
}

type ModuleStream struct {
	Module string `json:"module_name"`
	Stream string `json:"module_stream"`
}

type DbChange struct {
	ErrataChanges time.Time `json:"errata_changes"`
	CveChanges    time.Time `json:"cve_changes"`
	RepoChanges   time.Time `json:"repository_changes"`
	LastChange    time.Time `json:"last_change"`
	Exported      time.Time `json:"exported"`
}

type ErrataDetail struct {
	Synopsis     string
	Summary      sql.NullString
	Type         string
	Severity     sql.NullString
	Description  sql.NullString
	CVEs         []int
	PkgIds       []int
	ModulePkgIds []int
	Bugzillas    []string
	Refs         []string
	Modules      []Module
	Solution     sql.NullString
	Issued       time.Time
	Updated      time.Time
	Url          string
}
