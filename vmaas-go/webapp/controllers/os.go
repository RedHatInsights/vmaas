package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

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
