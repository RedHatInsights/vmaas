package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// RPMPkgNamesHandler godoc
//
//	@Summary		Get a list of content sets by RPM name
//	@Description	Get a list of content sets by RPM name.
//	@Produce		json
//	@Param			rpm	path	string	true	"RPM name"
//	@Success		200	{object}	vmaas.RPMPkgNames
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/package_names/rpms/{rpm} [get]
func RPMPkgNamesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	name := c.Param("rpm")
	req := vmaas.RPMPkgNamesRequest{RPMNames: []string{name}}

	res, err := core.VmaasAPI.RPMPkgNames(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// RPMPkgNamesPostHandler godoc
//
//	@Summary		Get a list of content sets by RPM name and content sets
//	@Description	Get a list of content sets by RPM name and content sets.
//	@Accept			json
//	@Produce		json
//	@Param			rpm_name_list	body	vmaas.RPMPkgNamesRequest	true	"rpm_name_list"
//	@Success		200	{object}	vmaas.RPMPkgNames
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/package_names/rpms [post]
func RPMPkgNamesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.RPMPkgNamesRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	res, err := core.VmaasAPI.RPMPkgNames(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// SRPMPkgNamesHandler godoc
//
//	@Summary		Get content sets with associated RPM names by SRPM
//	@Description	Get content sets with associated RPM names by SRPM.
//	@Produce		json
//	@Param			srpm	path	string	true	"SRPM name"
//	@Success		200	{object}	vmaas.SRPMPkgNames
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/package_names/srpms/{srpm} [get]
func SRPMPkgNamesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	name := c.Param("srpm")
	req := vmaas.SRPMPkgNamesRequest{SRPMNames: []string{name}}

	res, err := core.VmaasAPI.SRPMPkgNames(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// SRPMPkgNamesPostHandler godoc
//
//	@Summary		Get content sets with associated RPM names by SRPM and content sets
//	@Description	Get content sets with associated RPM names by SRPM and content sets.
//	@Accept			json
//	@Produce		json
//	@Param			srpm_name_list	body	vmaas.SRPMPkgNamesRequest	true	"srpm_name_list"
//	@Success		200	{object}	vmaas.SRPMPkgNames
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/package_names/srpms [post]
func SRPMPkgNamesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.SRPMPkgNamesRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	res, err := core.VmaasAPI.SRPMPkgNames(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}
