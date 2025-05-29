package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// PkgTreeHandler godoc
//
//	@Summary		Get NEVRA tree for a package name
//	@Description	Get NEVRA tree for a package name. It is possible to use a POSIX regular expression as a pattern for package names.
//	@Produce		json
//	@Param			package_name	path	string	true	"package name"
//	@Success		200	{object}	vmaas.PkgTree
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/pkgtree/{package_name} [get]
//
//nolint:lll
func PkgTreeHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	pkg := c.Param("package_name")
	req := vmaas.PkgTreeRequest{PackageNames: []string{pkg}}

	res, err := core.VmaasAPI.PkgTree(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// PkgTreePostHandler godoc
//
//	@Summary		Get NEVRA trees for package names
//	@Description	Get NEVRA trees for package names. Use `package_name_list` parameter to provide a list of package names, or a single POSIX regular expression.
//	@Accept			json
//	@Produce		json
//	@Param			package_name_list	body	vmaas.PkgTreeRequest	true	"package_name_list"
//	@Success		200	{object}	vmaas.PkgTree
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/pkgtree [post]
//
//nolint:lll
func PkgTreePostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.PkgTreeRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	res, err := core.VmaasAPI.PkgTree(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}
