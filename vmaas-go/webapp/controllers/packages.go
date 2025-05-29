package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// PackagesHandler godoc
//
//	@Summary		Get details for a package
//	@Description	Get details about a package.
//	@Produce		json
//	@Param			nevra	path	string	true	"NEVRA"
//	@Success		200	{object}	vmaas.Packages
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/packages/{nevra} [get]
func PackagesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	pkg := c.Param("nevra")
	req := vmaas.PackagesRequest{Packages: []string{pkg}}

	res, err := core.VmaasAPI.Packages(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// PackagesPostHandler godoc
//
//	@Summary		Get details for packages
//	@Description	Get details about packages. Use `package_list` to provide a list of package NEVRAs.
//	@Accept			json
//	@Produce		json
//	@Param			package_list	body	vmaas.PackagesRequest	true	"package_list"
//	@Success		200	{object}	vmaas.Packages
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/packages [post]
func PackagesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.PackagesRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	res, err := core.VmaasAPI.Packages(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}
