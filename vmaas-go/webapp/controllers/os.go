package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// OSHandler godoc
//
//	@Summary		Get OS vulnerability report
//	@Description	get OS vulnerability report
//	@Produce		json
//	@Success		200	{object}	vmaas.VulnerabilityReport
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/os/vulnerability/report [get]
func OSHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}

	res, err := core.VmaasAPI.OSVulnerabilityReport()
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}
