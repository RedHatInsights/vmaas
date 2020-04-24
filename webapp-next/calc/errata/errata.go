package errata

import (
	"app/cache"
	"app/calc"
	"github.com/pkg/errors"
	"time"
)

type Request struct {
	ErrataList    []string   `json:"errata_list"`
	ModifiedSince *time.Time `json:"modified_since"`
	calc.RequestPaging
}

func (r Request) Validate() (int, error) {
	if r.ErrataList == nil {
		return 400, errors.New("'repo_list' is a required property")
	}
	if len(r.ErrataList) == 0 {
		return 400, errors.New("[] is too short - 'repo_list'")
	}
	return 200, nil
}

type ErratumInfo struct {
	Severity          *string  `json:"severity"`
	Type              string   `json:"type"`
	ReferenceList     []string `json:"reference_list"`
	Updated           string   `json:"updated"`
	Issued            string   `json:"issued"`
	Description       *string  `json:"description"`
	Summary           *string  `json:"summary"`
	Url               string   `json:"url"`
	Synopsis          string   `json:"synopsis"`
	CveList           []string `json:"cve_list"`
	BugzillaList      []string `json:"bugzilla_list"`
	PackageList       []string `json:"package_list"`
	SourcePackageList []string `json:"source_package_list"`
}

type Response struct {
	calc.ResponsePaging
	ErrataList    *map[string]ErratumInfo `json:"errata_list,omitempty"`
	ModifiedSince string                  `json:"modified_since,omitempty"`
}

func FindByRegex(cache *cache.Cache, reg string) ([]string, error) {
	re, err := calc.AnchorRegex(reg)
	if err != nil {
		return nil, err
	}
	res := []string{}
	for c := range cache.ErrataDetail {
		if re.MatchString(c) {
			res = append(res, c)
		}
	}
	return res, nil
}

func CalcErrata(c *cache.Cache, req Request) (*Response, error) {
	var err error
	resp := Response{
		ErrataList: &map[string]ErratumInfo{},
	}

	if len(req.ErrataList) == 0 {
		return &resp, nil
	}

	if len(req.ErrataList) == 1 {
		req.ErrataList, err = FindByRegex(c, req.ErrataList[0])
		if err != nil {
			return nil, err
		}
	}

	pageToProcess, paging := calc.PaginateStrings(req.ErrataList, req.RequestPaging, func(erratum string) bool {
		det, has := c.ErrataDetail[erratum]
		if !has {
			return false
		}

		// TODO: Check logic
		return req.ModifiedSince == nil ||
			((det.Updated != nil && det.Updated.After(*req.ModifiedSince)) ||
				(det.Issued != nil && det.Issued.After(*req.ModifiedSince)))
	})

	for _, erratum := range pageToProcess {
		det := c.ErrataDetail[erratum]
		binaries, sources := calc.PackagesSplitByType(c, det.PkgIds)

		cves := []string{}
		for _, cveId := range det.CVEs {
			cves = append(cves, c.CveNames[cveId])
		}

		(*resp.ErrataList)[erratum] = ErratumInfo{
			Type:              det.Type,
			Severity:          det.Severity,
			ReferenceList:     det.Refs,
			Updated:           calc.NilToEmpty(calc.FormatDateOpt(det.Updated)),
			Issued:            calc.NilToEmpty(calc.FormatDateOpt(det.Issued)),
			Description:       det.Description,
			Summary:           det.Summary,
			Url:               det.Url,
			Synopsis:          det.Synopsis,
			CveList:           cves,
			BugzillaList:      det.Bugzillas,
			PackageList:       binaries,
			SourcePackageList: sources,
		}

	}

	resp.ResponsePaging = paging
	return &resp, nil
}
