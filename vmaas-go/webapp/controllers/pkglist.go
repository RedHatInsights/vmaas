package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// PkgListPostHandler godoc
//
//	@Summary		Get details for all packages
//	@Description	Get details for all packages.
//	@Accept			json
//	@Produce		json
//	@Success		200	{object}	vmaas.PkgList
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/pkglist [post]
func PkgListPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.PkgListRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	res := core.VmaasAPI.PkgList(&req)
	c.JSON(http.StatusOK, res)
}
