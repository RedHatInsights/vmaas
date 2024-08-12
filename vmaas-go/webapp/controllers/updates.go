package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

func UpdatesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	pkg := c.Param("package")
	request := vmaas.Request{Packages: []string{pkg}}

	updates, err := core.VmaasAPI.Updates(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, updates)
}

func UpdatesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	request := vmaas.Request{}
	err := bindValidateJSON(c, &request)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	updates, err := core.VmaasAPI.Updates(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, updates)
}
