package cache

import (
	"app/utils"
	"database/sql"
	"fmt"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"sort"
	"sync"
	"time"
)

var (
	lock = &sync.Mutex{}
	db   *gorm.DB
	C    *Cache
)

func openDb(path string) {
	tmpDb, err := gorm.Open("sqlite3", path)
	if err != nil {
		panic(err)
	}
	db = tmpDb
}

// Make sure only one load at a time is performed
func LoadCache(path string) *Cache {
	lock.Lock()

	openDb(path)
	c := Cache{}
	c.Id2Packagename, c.Packagename2Id = loadPkgNames()
	c.Updates = loadUpdates()
	c.UpdatesIndex = loadUpdatesIndex()

	c.Id2Evr, c.Evr2Id = loadEvrMaps()
	c.Id2Arch, c.Arch2Id = loadArchs()
	c.ArchCompat = loadArchCompat()

	c.PackageDetails, c.Nevra2PkgId, c.SrcPkgId2PkgId = loadPkgDetails("PackageDetails, Nevra2PkgId, SrcPkgId2PkgId")

	c.RepoDetails, c.RepoLabel2Ids, c.ProductId2RepoIds = loadRepoDetails("RepoDetails, RepoLabel2Ids, ProductId2RepoIds")

	c.PkgId2RepoIds = loadPkgRepos()
	c.ErrataDetail, c.ErrataId2Name = loadErratas("ErrataDetail, ErrataId2Name")
	c.PkgId2ErrataIds = LoadPkgErratas()
	c.ErrataId2RepoIds = loadErrataRepoIds()
	c.CveDetail, c.CveNames = loadCves("CveDetail")
	c.PkgErrata2Module = loadPkgErrataModule("PkgErrata2Module")
	c.ModuleName2Ids = loadModuleName2Ids("ModuleName2Ids")
	c.DbChange = loadDbChanges("DbChange")
	c.String = loadString("String")

	lock.Unlock()
	return &c
}

func loadErrataRepoIds() map[ErrataID][]RepoID {
	res := make(map[ErrataID][]RepoID)
	for k, v := range loadInt2Ints("errata_repo", "errata_id,repo_id", "ErrataId2RepoIds") {
		id := ErrataID(k)
		for _, i := range v {
			res[id] = append(res[id], RepoID(i))
		}
	}
	return res
}

func LoadPkgErratas() (map[PkgID][]ErrataID) {
	pkgToErrata := make(map[PkgID][]ErrataID)
	for k, v := range loadInt2Ints("pkg_errata", "pkg_id,errata_id", "PkgId2ErrataIds") {
		id := PkgID(k)
		for _, i := range v {
			pkgToErrata[id] = append(pkgToErrata[id], ErrataID(i))
		}
	}

	return pkgToErrata
}

func loadPkgRepos() map[PkgID][]RepoID {
	defer utils.TimeTrack(time.Now(), "PkgRepos")

	res := map[PkgID][]RepoID{}
	doForRows("select pkg_id, repo_id from pkg_repo", func(row *sql.Rows) {
		var n PkgID
		var p RepoID
		err := row.Scan(&n, &p)
		if err != nil {
			panic(err)
		}
		res[n] = append(res[n], p)
	})
	return res
}

func loadPkgNames() (map[NameID]string, map[string]NameID) {
	defer utils.TimeTrack(time.Now(), "PkgNames")

	type PkgName struct {
		Id          NameID
		Packagename string
	}

	var rows []PkgName
	err := db.Table("packagename").Find(&rows).Error
	if err != nil {
		panic(err)
	}
	id2name := map[NameID]string{}
	name2id := map[string]NameID{}

	for _, r := range rows {
		id2name[r.Id] = r.Packagename
		name2id[r.Packagename] = r.Id
	}
	return id2name, name2id
}

func loadUpdates() map[NameID][]PkgID {
	defer utils.TimeTrack(time.Now(), "Updates")

	res := map[NameID][]PkgID{}
	doForRows("select name_id, package_id from updates order by package_order", func(row *sql.Rows) {
		var n NameID
		var p PkgID
		err := row.Scan(&n, &p)
		if err != nil {
			panic(err)
		}
		res[n] = append(res[n], p)
	})
	return res
}

func loadUpdatesIndex() map[NameID]map[EvrID][]int {
	defer utils.TimeTrack(time.Now(), "Updates index")
	res := map[NameID]map[EvrID][]int{}
	doForRows("select name_id, evr_id, package_order from updates_index order by package_order", func(row *sql.Rows) {
		var n NameID
		var e EvrID
		var o int
		err := row.Scan(&n, &e, &o)
		if err != nil {
			panic(err)
		}
		nmap := res[n]
		if nmap == nil {
			nmap = map[EvrID][]int{}
		}
		nmap[e] = append(nmap[e], o)
		res[n] = nmap
	})
	return res
}

func getAllRows(tableName, cols, orderBy string) *sql.Rows {
	rows, err := db.DB().Query(fmt.Sprintf("SELECT %s FROM %s ORDER BY %s",
		cols, tableName, orderBy))
	if err != nil {
		panic(err)
	}
	return rows
}

func doForRows(q string, f func(row *sql.Rows)) {
	rows, err := db.DB().Query(q)
	if err != nil {
		panic(err)
	}

	for rows.Next() {
		f(rows)
	}
}

func loadIntArray(tableName, col, orderBy string) []int {
	rows := getAllRows(tableName, col, orderBy)
	defer rows.Close()

	var arr []int
	for rows.Next() {
		var num int
		err := rows.Scan(&num)
		if err != nil {
			panic(err)
		}

		arr = append(arr, num)
	}
	return arr
}

func loadStrArray(tableName, col, orderBy string) []string {
	rows := getAllRows(tableName, col, orderBy)
	defer rows.Close()

	var arr []string
	for rows.Next() {
		var val string
		err := rows.Scan(&val)
		if err != nil {
			panic(err)
		}

		arr = append(arr, val)
	}
	return arr
}

func loadEvrMaps() (map[EvrID]Evr, map[Evr]EvrID) {
	defer utils.TimeTrack(time.Now(), "EVR")

	type IdEvr struct {
		ID EvrID
		Evr
	}

	var rows []IdEvr
	err := db.Table("evr").Find(&rows).Error
	if err != nil {
		panic(err)
	}

	id2evr := map[EvrID]Evr{}
	evr2id := map[Evr]EvrID{}

	for _, r := range rows {
		id2evr[r.ID] = r.Evr
		evr2id[r.Evr] = r.ID
	}
	return id2evr, evr2id
}

func loadArchs() (map[ArchID]string, map[string]ArchID) {
	defer utils.TimeTrack(time.Now(), "Arch")

	type Arch struct {
		ID   ArchID
		Arch string
	}
	var rows []Arch
	err := db.Table("arch").Find(&rows).Error
	if err != nil {
		panic(err)
	}

	id2arch := map[ArchID]string{}
	arch2id := map[string]ArchID{}

	for _, r := range rows {
		id2arch[r.ID] = r.Arch
		arch2id[r.Arch] = r.ID
	}
	return id2arch, arch2id
}
func loadArchCompat() map[ArchID]map[ArchID]bool {
	defer utils.TimeTrack(time.Now(), "ArchCompat")

	type ArchCompat struct {
		FromArchId ArchID
		ToArchId   ArchID
	}
	var rows []ArchCompat
	err := db.Table("arch_compat").Find(&rows).Error
	if err != nil {
		panic(err)
	}

	m := map[ArchID]map[ArchID]bool{}

	for _, r := range rows {
		fromMap := m[r.FromArchId]
		if fromMap == nil {
			fromMap = map[ArchID]bool{}
		}
		fromMap[r.ToArchId] = true
		m[r.FromArchId] = fromMap
	}
	return m
}

func loadPkgDetails(info string) (map[PkgID]PackageDetail, map[Nevra]PkgID, map[PkgID][]PkgID) {
	defer utils.TimeTrack(time.Now(), info)

	rows := getAllRows("package_detail", "*", "ID")
	id2pkdDetail := map[PkgID]PackageDetail{}
	nevra2id := map[Nevra]PkgID{}
	srcPkgId2PkgId := map[PkgID][]PkgID{}
	for rows.Next() {
		var pkgId PkgID
		var det PackageDetail
		err := rows.Scan(&pkgId, &det.NameId, &det.EvrId, &det.ArchId, &det.SummaryId, &det.DescriptionId,
			&det.SrcPkgId)
		if err != nil {
			panic(err)
		}
		id2pkdDetail[pkgId] = det

		nevra := Nevra{det.NameId, det.EvrId, det.ArchId}
		nevra2id[nevra] = pkgId

		if det.SrcPkgId == nil {
			continue
		}

		_, ok := srcPkgId2PkgId[*det.SrcPkgId]
		if !ok {
			srcPkgId2PkgId[*det.SrcPkgId] = []PkgID{}
		}

		srcPkgId2PkgId[*det.SrcPkgId] = append(srcPkgId2PkgId[*det.SrcPkgId], pkgId)
	}
	return id2pkdDetail, nevra2id, srcPkgId2PkgId
}

func loadRepoDetails(info string) (map[RepoID]RepoDetail, map[string][]RepoID, map[int][]RepoID) {
	defer utils.TimeTrack(time.Now(), info)

	rows := getAllRows("repo_detail", "*", "label")
	id2repoDetail := map[RepoID]RepoDetail{}
	repoLabel2id := map[string][]RepoID{}
	prodId2RepoIds := map[int][]RepoID{}
	for rows.Next() {
		var repoId RepoID
		var det RepoDetail

		err := rows.Scan(&repoId, &det.Label, &det.Name, &det.Url, &det.BaseArch, &det.ReleaseVer,
			&det.Product, &det.ProductId, &det.Revision)
		if err != nil {
			panic(err)
		}

		id2repoDetail[repoId] = det

		_, ok := repoLabel2id[det.Label]
		if !ok {
			repoLabel2id[det.Label] = []RepoID{}
		}
		repoLabel2id[det.Label] = append(repoLabel2id[det.Label], repoId)

		_, ok = prodId2RepoIds[det.ProductId]
		if !ok {
			prodId2RepoIds[det.ProductId] = []RepoID{}
		}
		prodId2RepoIds[det.ProductId] = append(prodId2RepoIds[det.ProductId], repoId)
	}
	return id2repoDetail, repoLabel2id, prodId2RepoIds
}

func loadErratas(info string) (map[string]ErrataDetail, map[ErrataID]string) {
	defer utils.TimeTrack(time.Now(), info)

	erId2cves := loadInt2Ints("errata_cve", "errata_id,cve_id", "erId2cves")
	erId2pkgIds := loadInt2Ints("pkg_errata", "errata_id,pkg_id", "erId2pkgId")
	erId2modulePkgIds := loadInt2Ints("errata_modulepkg", "errata_id,pkg_id", "erId2modulePkgIds")
	erId2bzs := loadInt2Strings("errata_bugzilla", "errata_id,bugzilla", "erId2bzs")
	erId2refs := loadInt2Strings("errata_refs", "errata_id,ref", "erId2refs")
	erId2modules := loadErrataModules()

	cols := "ID,name,synopsis,summary,type,severity,description,solution,issued,updated,url"
	rows := getAllRows("errata_detail", cols, "ID")
	errataDetail := map[string]ErrataDetail{}
	errataId2Name := map[ErrataID]string{}
	for rows.Next() {
		var errataId ErrataID
		var errataName string
		var det ErrataDetail
		err := rows.Scan(&errataId, &errataName, &det.Synopsis, &det.Summary, &det.Type, &det.Severity,
			&det.Description, &det.Solution, &det.Issued, &det.Updated, &det.Url)
		if err != nil {
			panic(err)
		}
		errataId2Name[errataId] = errataName

		det.ID = errataId
		if cves, ok := erId2cves[int(errataId)]; ok {
			det.CVEs = cves
		}

		if pkgIds, ok := erId2pkgIds[int(errataId)]; ok {
			det.PkgIds = pkgIds
		}

		if modulePkgIds, ok := erId2modulePkgIds[int(errataId)]; ok {
			det.ModulePkgIds = modulePkgIds
		}

		if bzs, ok := erId2bzs[int(errataId)]; ok {
			det.Bugzillas = bzs
		}

		if refs, ok := erId2refs[int(errataId)]; ok {
			det.Refs = refs
		}

		if modules, ok := erId2modules[int(errataId)]; ok {
			det.Modules = modules
		}
		errataDetail[errataName] = det
	}
	return errataDetail, errataId2Name
}

func loadCves(info string) (map[string]CveDetail, map[int]string) {
	defer utils.TimeTrack(time.Now(), info)

	cveId2cwes := loadInt2Strings("cve_cwe", "cve_id,cwe", "cveId2cwes")
	cveId2pkg := loadInt2Ints("cve_pkg", "cve_id,pkg_id", "cveId2pkg")
	cve2eid := loadInt2Ints("errata_cve", "cve_id,errata_id", "cve2eid")

	rows := getAllRows("cve_detail", "*", "id")
	cveDetails := map[string]CveDetail{}
	cveNames := map[int]string{}
	for rows.Next() {
		var cveId int
		var cveName string
		var det CveDetail
		err := rows.Scan(&cveId, &cveName, &det.RedHatUrl, &det.SecondaryUrl, &det.Cvss3Score, &det.Cvss3Metrics,
			&det.Impact, &det.PublishedDate, &det.ModifiedDate, &det.Iava, &det.Description, &det.Cvss2Score,
			&det.Cvss2Metrics, &det.Source)
		if err != nil {
			panic(err)
		}

		cwes, ok := cveId2cwes[cveId]
		sort.Strings(cwes)
		if ok {
			det.CWEs = cwes
		}

		pkgs, ok := cveId2pkg[cveId]
		if ok {
			det.PkgIds = pkgs
		}

		eids, ok := cve2eid[cveId]
		if ok {
			det.ErrataIds = eids
		}
		cveDetails[cveName] = det
		cveNames[cveId] = cveName
	}
	return cveDetails, cveNames
}

func loadPkgErrataModule(info string) map[PkgErrata][]int {
	defer utils.TimeTrack(time.Now(), info)

	orderBy := "pkg_id,errata_id,module_stream_id"
	table := "errata_modulepkg"
	pkgIds := loadIntArray(table, "pkg_id", orderBy)
	errataIds := loadIntArray(table, "errata_id", orderBy)
	moduleStreamIds := loadIntArray(table, "module_stream_id", orderBy)

	m := map[PkgErrata][]int{}

	for i := 0; i < len(pkgIds); i++ {
		pkgErrata := PkgErrata{pkgIds[i], errataIds[i]}
		_, ok := m[pkgErrata]
		if !ok {
			m[pkgErrata] = []int{}
		}

		m[pkgErrata] = append(m[pkgErrata], moduleStreamIds[i])
	}
	return m
}

func loadModuleName2Ids(info string) map[ModuleStream][]int {
	defer utils.TimeTrack(time.Now(), info)

	orderBy := "module,stream"
	table := "module_stream"
	modules := loadStrArray(table, "module", orderBy)
	streams := loadStrArray(table, "stream", orderBy)
	streamIds := loadIntArray(table, "stream_id", orderBy)

	m := map[ModuleStream][]int{}

	for i := 0; i < len(modules); i++ {
		pkgErrata := ModuleStream{modules[i], streams[i]}
		_, ok := m[pkgErrata]
		if !ok {
			m[pkgErrata] = []int{}
		}

		m[pkgErrata] = append(m[pkgErrata], streamIds[i])
	}
	return m
}

func loadString(info string) map[int]string {
	defer utils.TimeTrack(time.Now(), info)

	rows := getAllRows("string", "*", "ID")
	m := map[int]string{}
	for rows.Next() {
		var id int
		var str *string
		err := rows.Scan(&id, &str)
		if err != nil {
			panic(err)
		}
		if str != nil {
			m[id] = *str
		}
	}
	return m
}

func loadDbChanges(info string) DbChange {
	defer utils.TimeTrack(time.Now(), info)

	rows := getAllRows("dbchange", "*", "errata_changes")
	arr := []DbChange{}
	for rows.Next() {
		var item DbChange
		err := rows.Scan(&item.ErrataChanges, &item.CveChanges, &item.RepoChanges,
			&item.LastChange, &item.Exported)
		if err != nil {
			panic(err)
		}
		arr = append(arr, item)
	}
	return arr[0]
}

func loadInt2Ints(table, cols, info string) map[int][]int {
	defer utils.TimeTrack(time.Now(), info)

	rows := getAllRows(table, cols, cols)
	int2ints := map[int][]int{}
	for rows.Next() {
		var key int
		var val int
		err := rows.Scan(&key, &val)
		if err != nil {
			panic(err)
		}

		_, ok := int2ints[key]
		if !ok {
			int2ints[key] = []int{}
		}
		int2ints[key] = append(int2ints[key], val)
	}
	return int2ints
}

func loadInt2Strings(table, cols, info string) map[int][]string {
	defer utils.TimeTrack(time.Now(), info)

	rows := getAllRows(table, cols, cols)
	int2strs := map[int][]string{}
	for rows.Next() {
		var key int
		var val string
		err := rows.Scan(&key, &val)
		if err != nil {
			panic(err)
		}

		_, ok := int2strs[key]
		if !ok {
			int2strs[key] = []string{}
		}

		int2strs[key] = append(int2strs[key], val)
	}
	return int2strs
}

func loadString2Ints(table, cols, info string) map[string][]int {
	defer utils.TimeTrack(time.Now(), info)

	rows := getAllRows(table, cols, cols)
	int2strs := map[string][]int{}
	for rows.Next() {
		var key string
		var val int
		err := rows.Scan(&key, &val)
		if err != nil {
			panic(err)
		}

		_, ok := int2strs[key]
		if !ok {
			int2strs[key] = []int{}
		}

		int2strs[key] = append(int2strs[key], val)
	}
	return int2strs
}

type Module struct {
	Name              string
	Stream            string
	Version           string
	Context           string
	PackageList       []string
	SourcePackageList []string
}

func loadErrataModules() map[int][]Module {
	defer utils.TimeTrack(time.Now(), "errata2module")

	rows := getAllRows("errata_module", "*", "errata_id")

	erId2modules := map[int][]Module{}
	for rows.Next() {
		var erId int
		var mod Module
		err := rows.Scan(&erId, &mod.Name, &mod.Stream, &mod.Version, &mod.Context)
		if err != nil {
			panic(err)
		}

		_, ok := erId2modules[erId]
		if !ok {
			erId2modules[erId] = []Module{}
		}

		erId2modules[erId] = append(erId2modules[erId], mod)
	}
	return erId2modules
}
