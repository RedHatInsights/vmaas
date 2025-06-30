package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/core"
)

// DBChangeHandler godoc
//
//	@Summary		Get last-updated times from VMaaS DB
//	@Description	Get last-updated times from VMaaS DB.
//	@Produce		json
//	@Success		200	{object}	vmaas.DBChange
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/dbchange [get]
func DBChangeHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}

	res := core.VmaasAPI.DBChange()
	c.JSON(http.StatusOK, res)
}
