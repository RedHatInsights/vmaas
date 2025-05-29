package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// VulnerabilitiesHandler godoc
//
//	@Summary		Get vulnerabilities for a package
//	@Description	Get a list of applicable CVEs for a single package NEVRA.
//	@Produce		json
//	@Param			package	path	string	true	"NEVRA"
//	@Success		200	{object}	vmaas.Vulnerabilities
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/vulnerabilities/{package} [get]
func VulnerabilitiesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	pkg := c.Param("package")
	request := vmaas.Request{Packages: []string{pkg}}

	vulnerabilities, err := core.VmaasAPI.Vulnerabilities(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, vulnerabilities)
}

// VulnerabilitiesPostHandler godoc
//
//	@Summary		Get vulnerabilities for packages
//	@Description	Get a list of applicable CVEs for a package list.
//	@Accept			json
//	@Produce		json
//	@Param			package_list	body	vmaas.Request	true	"package_list"
//	@Success		200	{object}	vmaas.Vulnerabilities
//	@Success		200	{object}	vmaas.VulnerabilitiesExtended	"if request.extended"
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/vulnerabilities [post]
func VulnerabilitiesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	request := vmaas.Request{}
	err := bindValidateJSON(c, &request)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	if request.Extended {
		vulnerabilities, err := core.VmaasAPI.VulnerabilitiesExtended(&request)
		if err != nil {
			utils.LogAndRespError(c, err)
			return
		}
		c.JSON(http.StatusOK, vulnerabilities)
		return
	}

	vulnerabilities, err := core.VmaasAPI.Vulnerabilities(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, vulnerabilities)
}
