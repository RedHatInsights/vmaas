package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// PatchesHandler godoc
//
//	@Summary		Get patches for a package
//	@Description	Get a list of applicable errata for a package.
//	@Produce		json
//	@Param			nevra	path	string	true	"NEVRA"
//	@Success		200	{object}	vmaas.Patches
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/patches/{nevra} [get]
func PatchesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	patch := c.Param("nevra")
	req := vmaas.Request{Packages: []string{patch}}

	res, err := core.VmaasAPI.Patches(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// PatchesPostHandler godoc
//
//	@Summary		Get patches for packages
//	@Description	Get a list of applicable errata for a package list.
//	@Accept			json
//	@Produce		json
//	@Param			package_list	body	vmaas.Request	true	"package_list"
//	@Success		200	{object}	vmaas.Patches
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/patches [post]
func PatchesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.Request{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	res, err := core.VmaasAPI.Patches(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}
