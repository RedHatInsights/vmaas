package cves

import (
	"app/cache"
	"app/calc"
	"errors"
	"strconv"
	"time"
)

type FormatFloat float64

func (f FormatFloat) MarshalJSON() ([]byte, error) {
	if float64(f) == float64(int(f)) {
		return []byte(strconv.FormatFloat(float64(f), 'f', 3, 64)), nil
	}
	return []byte(strconv.FormatFloat(float64(f), 'f', -3, 64)), nil
}

type Request struct {
	CveList        []string   `json:"cve_list"`
	ModifiedSince  *time.Time `json:"modified_since"`
	PublishedSince *time.Time `json:"published_since"`
	RhOnly         bool       `json:"rh_only"`
	calc.RequestPaging
}

func (r Request) Validate() (int, error) {
	if r.CveList == nil {
		return 400, errors.New("'cve_list' is a required property")
	}
	if len(r.CveList) == 0 {
		return 400, errors.New("[] is too short - 'cve_list'")
	}
	return 200, nil
}

type CveInfo struct {
	Impact string `json:"impact"`

	Synopsis    string `json:"synopsis"`
	Description string `json:"description"`

	PublicDate   string `json:"public_date"`
	ModifiedDate string `json:"modified_date"`
	RedhatURL    string `json:"redhat_url"`
	SecondaryURL string `json:"secondary_url"`

	Cvss2Score        string   `json:"cvss2_score"`
	Cvss2Metrics      string   `json:"cvss2_metrics"`
	Cvss3Score        string   `json:"cvss3_score"`
	Cvss3Metrics      string   `json:"cvss3_metrics"`
	CweList           []string `json:"cwe_list"`
	ErrataList        []string `json:"errata_list"`
	PackageList       []string `json:"package_list"`
	SourcePackageList []string `json:"source_package_list"`
}

type Response struct {
	calc.ResponsePaging
	CveList        *map[string]CveInfo `json:"cve_list,omitempty"`
	ModifiedSince  string              `json:"modified_since,omitempty"`
	PublishedSince string              `json:"published_since,omitempty"`
}

func FindByRegex(cache *cache.Cache, reg string) ([]string, error) {
	re, err := calc.AnchorRegex(reg)
	if err != nil {
		return nil, err
	}
	res := []string{}
	for c := range cache.CveDetail {
		if re.MatchString(c) {
			res = append(res, c)
		}
	}
	return res, nil
}

func CalcCves(c *cache.Cache, req Request) (*Response, error) {
	var err error
	resp := Response{
		CveList: &map[string]CveInfo{},
	}

	if len(req.CveList) == 0 {
		return &resp, nil
	}

	if len(req.CveList) == 1 {
		req.CveList, err = FindByRegex(c, req.CveList[0])
		if err != nil {
			return nil, err
		}
	}

	pageToProcess, paging := calc.PaginateStrings(req.CveList, req.RequestPaging, func(cve string) bool {
		det := c.CveDetail[cve]
		shouldStay :=
			req.ModifiedSince == nil ||
				(det.ModifiedDate != nil && det.ModifiedDate.After(*req.ModifiedSince) ||
					(det.PublishedDate != nil && det.PublishedDate.After(*req.ModifiedSince)))

		shouldStay = shouldStay &&
			(req.PublishedSince == nil || (det.PublishedDate != nil && det.PublishedDate.After(*req.PublishedSince)))

		shouldStay = shouldStay &&
			(!req.RhOnly || det.Source == "Red Hat")

		return shouldStay
	})

	for _, cve := range pageToProcess {
		det, has := c.CveDetail[cve]
		if !has {
			continue
		}
		binaries, sources := calc.PackagesSplitByType(c, det.PkgIds)
		errata := []string{}
		for _, e := range det.ErrataIds {
			errata = append(errata, c.ErrataId2Name[cache.ErrataID(e)])
		}

		if det.CWEs == nil {
			det.CWEs = []string{}
		}

		(*resp.CveList)[cve] = CveInfo{
			Impact:            det.Impact,
			Synopsis:          cve,
			Description:       det.Description,
			PublicDate:        calc.NilToEmpty(calc.FormatDateOpt(det.PublishedDate)),
			ModifiedDate:      calc.NilToEmpty(calc.FormatDateOpt(det.ModifiedDate)),
			RedhatURL:         calc.NilToEmpty(det.RedHatUrl),
			SecondaryURL:      calc.NilToEmpty(det.SecondaryUrl),
			Cvss2Score:        calc.NilToEmpty(det.Cvss2Score),
			Cvss2Metrics:      calc.NilToEmpty(det.Cvss2Metrics),
			Cvss3Score:        calc.NilToEmpty(det.Cvss3Score),
			Cvss3Metrics:      calc.NilToEmpty(det.Cvss3Metrics),
			CweList:           det.CWEs,
			PackageList:       binaries,
			SourcePackageList: sources,
			ErrataList:        errata,
		}

	}

	resp.ResponsePaging = paging
	resp.ModifiedSince = calc.NilToEmpty(calc.FormatDateOpt(req.ModifiedSince))
	resp.PublishedSince = calc.NilToEmpty(calc.FormatDateOpt(req.PublishedSince))
	return &resp, nil
}
