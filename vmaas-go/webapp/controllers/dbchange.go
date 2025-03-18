package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/core"
)

func DBChangeHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}

	res := core.VmaasAPI.DBChange()
	c.JSON(http.StatusOK, res)
}
