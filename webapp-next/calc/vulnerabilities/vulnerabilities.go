package vulnerabilities

import (
	"app/cache"
	"app/calc/updates"
	"sort"
)

type Request updates.Request

func (r Request) Validate() (int, error) {
	return updates.Request(r).Validate()
}



type Response struct {
	CveList []string `json:"cve_list"`
}

func CalcVulnerabilities(cache *cache.Cache, req Request) (*Response, error) {
	resp := Response{CveList: []string{}}

	vulns, err := updates.Updates(cache, updates.Request(req), false, true)
	if err != nil {
		return nil, err
	}
	errata := map[string]bool{}
	cves := map[string]bool{}

	for _, v := range vulns.UpdateList {
		if v.AvailableUpdates == nil {
			continue
		}
		for _, up := range *v.AvailableUpdates {
			errata[up.Erratum] = true
		}
	}

	for n := range errata {
		for _, cve := range cache.ErrataDetail[n].CVEs {
			cves[cache.CveNames[cve]] = true
		}
	}

	for cve := range cves {
		resp.CveList = append(resp.CveList, cve)
	}
	sort.Strings(resp.CveList)

	return &resp, nil
}
