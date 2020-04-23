package calc

import (
	"app/cache"
	"app/utils"
	"github.com/gin-gonic/gin"
	"math"
	"sort"
	"time"
)

const DefaultPage = 1
const DefaultPageSize = 5000

type RequestPaging struct {
	Page     int `json:"page"`
	PageSize int `json:"page_size"`
}

type ResponsePaging struct {
	Page     int `json:"page"`
	PageSize int `json:"page_size"`
	Pages    int `json:"pages"`
}

func PaginateStrings(data []string, info RequestPaging, filter func(string) bool) ([]string, ResponsePaging) {
	sort.Strings(data)
	res := []string{}
	for _, d := range data {
		if filter == nil || filter(d) {
			res = append(res, d)
		}
	}
	if info.Page <= 0 {
		info.Page = DefaultPage
	}
	if info.PageSize <= 0 {
		info.PageSize = DefaultPageSize
	}

	start := (info.Page - 1) * info.PageSize
	end := info.Page * info.PageSize
	if end > len(res) {
		end = len(res)
	}

	pages := int(math.Ceil(float64(len(res)) / float64(info.PageSize)))
	res = res[start: end]

	return res, ResponsePaging{
		Page:     info.Page,
		PageSize: len(res),
		Pages:    pages,
	}
}

func FormatPackage(cache *cache.Cache, detail cache.PackageDetail) string {
	name := cache.Id2Packagename[detail.NameId]
	evr := cache.Id2Evr[detail.EvrId]
	arch := cache.Id2Arch[detail.ArchId]
	return utils.FormatNevra(name, evr.Epoch, evr.Version, evr.Release, arch)
}

func PackagesSplitByType(c *cache.Cache, packages []int) (binary []string, src []string) {
	binary = []string{}
	src = []string{}
	for _, p := range packages {
		det := c.PackageDetails[cache.PkgID(p)]
		if det.ArchId == c.Arch2Id["src"] {
			src = append(src, FormatPackage(c, det))
		} else {
			binary = append(binary, FormatPackage(c, det))
		}
	}
	return
}

func NilToEmpty(s *string) string {
	if s != nil {
		return *s
	}
	return ""
}

func FormatDateOpt(d * time.Time) *string {
	if d != nil {
		res := d.String()
		return &res
	}
	return nil
}

func DBChange(c *gin.Context) {
	c.JSON(200, cache.C.DbChange)
}
