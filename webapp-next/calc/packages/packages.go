package packages

import (
	"app/cache"
	"app/calc"
	"app/utils"
	"github.com/pkg/errors"
)

type Request struct {
	PackageList []string `json:"package_list"`
	//calc.RequestPaging
}

func (r Request) Validate() (int, error) {
	if r.PackageList == nil {
		return 400, errors.New("'package_list' is a required property")
	}
	if len(r.PackageList) == 0 {
		return 400, errors.New("[] is too short - 'package_list'")
	}
	return 200, nil
}

type Response struct {
	//calc.ResponsePaging
	PackageList *map[string]PackageInfo `json:"package_list,omitempty"`
}
type PackageRepo struct {
	Label      string `json:"label"`
	Name       string `json:"name"`
	Basearch   string `json:"basearch"`
	Releasever string `json:"releasever"`
}

type PackageInfo struct {
	Summary       string        `json:"summary"`
	Description   string        `json:"description"`
	SourcePackage string        `json:"source_package"`
	PackageList   []string      `json:"package_list"`
	Repositories  []PackageRepo `json:"repositories"`
}

func getSourcePackage(c *cache.Cache, pkg cache.PackageDetail) string {
	var src string

	if pkg.SrcPkgId != nil {
		src = calc.FormatPackage(c, c.PackageDetails[*pkg.SrcPkgId])
	}
	return src
}

func getBinaryPackages(c *cache.Cache, pkgId cache.PkgID) []string {
	if ids, has := c.SrcPkgId2PkgId[pkgId]; has {
		res := []string{}
		for _, id := range ids {
			res = append(res, calc.FormatPackage(c, c.PackageDetails[id]))
		}
		return res
	}
	return []string{}
}

func CalcPackages(c *cache.Cache, req Request) (*Response, error) {
	var err error
	var has bool
	var nevra utils.Nevra
	var nameId cache.NameID
	var evrId cache.EvrID
	var archId cache.ArchID
	var pkgId cache.PkgID

	resp := Response{
		PackageList: &map[string]PackageInfo{},
	}

	if len(req.PackageList) == 0 {
		return &resp, nil
	}

	for _, pkg := range req.PackageList {
		if nevra, err = utils.ParseNevra(pkg); err != nil {
			return nil, err
		}
		if nameId, has = c.Packagename2Id[nevra.Name]; !has {
			continue
		}
		if evrId, has = c.Evr2Id[cache.Evr{nevra.Epoch, nevra.Version, nevra.Release}]; !has {
			continue
		}
		if archId, has = c.Arch2Id[nevra.Arch]; !has {
			continue
		}
		if pkgId, has = c.Nevra2PkgId[cache.Nevra{nameId, evrId, archId}]; !has {
			continue
		}

		det := c.PackageDetails[pkgId]

		repos := []PackageRepo{}
		if repoIds, has := c.PkgId2RepoIds[pkgId]; has {
			for _, rid := range repoIds {
				det := c.RepoDetails[rid]
				repos = append(repos, PackageRepo{
					Label:      det.Label,
					Name:       det.Name,
					Basearch:   calc.NilToEmpty(det.BaseArch),
					Releasever: calc.NilToEmpty(det.ReleaseVer),
				})
			}
		}

		(*resp.PackageList)[pkg] = PackageInfo{
			Summary:     c.String[det.SummaryId],
			Description: c.String[det.DescriptionId],

			SourcePackage: getSourcePackage(c, det),
			PackageList:   getBinaryPackages(c, pkgId),
			Repositories:  repos,
		}

	}

	return &resp, nil
}
