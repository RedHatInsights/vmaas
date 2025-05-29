package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// CvesHandler godoc
//
//	@Summary		Get details for a CVE
//	@Description	Get details for a CVE. It is possible to use a POSIX regular expression as a pattern for CVE names.
//	@Produce		json
//	@Param			cve	path	string	true	"CVE"
//	@Success		200				{object}	vmaas.Cves
//	@Failure		400,424,500,503	{object}	utils.ErrorResponse
//	@Router			/cves/{cve} [get]
func CvesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	cve := c.Param("cve")
	req := vmaas.CvesRequest{Cves: []string{cve}}

	res, err := core.VmaasAPI.Cves(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// CvesPostHandler godoc
//
//	@Summary		Get details for CVEs
//	@Description	Get details about CVEs with additional parameters. Use `cve_list` parameter to provide a list of CVE names, or a single POSIX regular expression.
//	@Accept			json
//	@Produce		json
//	@Param			cve_list	body	vmaas.CvesRequest	true	"cve_list"
//	@Success		200				{object}	vmaas.Cves
//	@Failure		400,424,500,503	{object}	utils.ErrorResponse
//	@Router			/cves [post]
//
//nolint:lll
func CvesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.CvesRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	cves, err := core.VmaasAPI.Cves(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, cves)
}
