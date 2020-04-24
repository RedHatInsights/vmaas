package repos

import (
	"app/cache"
	"app/calc"
	"errors"
	"time"
)

type Request struct {
	RepoList      []string   `json:"repository_list"`
	ModifiedSince *time.Time `json:"modified_since"`
	calc.RequestPaging
}

func (r Request) Validate() (int, error) {
	if r.RepoList == nil {
		return 400, errors.New("'repo_list' is a required property")
	}
	if len(r.RepoList) == 0 {
		return 400, errors.New("[] is too short - 'repo_list'")
	}
	return 200, nil
}

type RepoInfo struct {
	Product    string `json:"product"`
	Releasever string `json:"releasever"`
	Name       string `json:"name"`
	URL        string `json:"url"`
	BaseArch   string `json:"basearch"`
	Revision   string `json:"revision"`
	Label      string `json:"label"`
}

type Response struct {
	calc.ResponsePaging
	RepoList *map[string][]RepoInfo `json:"repository_list,omitempty"`
}

func FindByRegex(cache *cache.Cache, reg string) ([]string, error) {
	re, err := calc.AnchorRegex(reg)
	if err != nil {
		return nil, err
	}
	res := []string{}
	for c := range cache.RepoLabel2Ids {
		if re.MatchString(c) {
			res = append(res, c)
		}
	}
	return res, nil
}

func CalcRepos(c *cache.Cache, req Request) (*Response, error) {
	var err error
	resp := Response{
		RepoList: &map[string][]RepoInfo{},
	}

	if len(req.RepoList) == 0 {
		return &resp, nil
	}

	if len(req.RepoList) == 1 {
		req.RepoList, err = FindByRegex(c, req.RepoList[0])
		if err != nil {
			return nil, err
		}
	}

	pageToProcess, paging := calc.PaginateStrings(req.RepoList, req.RequestPaging, func(repo string) bool {
		for _, r := range c.RepoLabel2Ids[repo] {
			det := c.RepoDetails[r]

			if req.ModifiedSince == nil ||
				(det.Revision != nil && det.Revision.After(*req.ModifiedSince)) {
				return true
			}
		}
		return false
	})

	for _, repoLabel := range pageToProcess {
		for _, repoId := range c.RepoLabel2Ids[repoLabel] {
			det := c.RepoDetails[repoId]
			(*resp.RepoList)[repoLabel] = append((*resp.RepoList)[repoLabel],
				RepoInfo{
					Product:    det.Product,
					Releasever: calc.NilToEmpty(det.ReleaseVer),
					Name:       det.Name,
					URL:        det.Url,
					BaseArch:   calc.NilToEmpty(det.BaseArch),
					Revision:   calc.NilToEmpty(calc.FormatDateOpt(det.Revision)),
					Label:      det.Label,
				})
		}

	}

	resp.ResponsePaging = paging
	return &resp, nil
}
