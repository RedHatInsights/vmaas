package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/core"
)

// VersionHandler godoc
//
//	@Summary		Get VMaaS version
//	@Description	Get VMaaS version.
//	@Produce		json
//	@Success		200	{string}	string
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/version [get]
func VersionHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}

	res := core.VmaasAPI.Version()
	c.JSON(http.StatusOK, res)
}
