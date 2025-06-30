package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// UpdatesHandler godoc
//
//	@Summary		Get updates for a package
//	@Description	List all updates for single package NEVRA.
//	@Produce		json
//	@Param			package	path	string	true	"NEVRA"
//	@Success		200	{object}	vmaas.Updates
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/updates/{package} [get]
func UpdatesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	pkg := c.Param("package")
	request := vmaas.Request{Packages: []string{pkg}}

	updates, err := core.VmaasAPI.Updates(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, updates)
}

// UpdatesPostHandler godoc
//
//	@Summary		Get updates for packages
//	@Description	List all updates for list of package NEVRAs.
//	@Accept			json
//	@Produce		json
//	@Param			package_list	body	vmaas.Request	true	"package_list"
//	@Success		200	{object}	vmaas.Updates
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/updates [post]
func UpdatesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	request := vmaas.Request{}
	err := bindValidateJSON(c, &request)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	updates, err := core.VmaasAPI.Updates(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, updates)
}
