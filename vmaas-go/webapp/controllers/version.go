package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/core"
)

func VersionHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}

	res := core.VmaasAPI.Version()
	c.JSON(http.StatusOK, res)
}
