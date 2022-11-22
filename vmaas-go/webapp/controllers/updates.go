package controllers

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
)

func UpdatesHandler(c *gin.Context) {
	if core.VmaasAPI == nil {
		LogAndRespUnavailable(c, errors.New("data not available, please try again later"))
		return
	}
	pkg := c.Param("package")
	request := vmaas.Request{Packages: []string{pkg}}

	updates, err := core.VmaasAPI.Updates(&request)
	if err != nil {
		LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, updates)
}

func UpdatesPostHandler(c *gin.Context) {
	request, err := bindValidateJSON(c)
	if err != nil {
		LogAndRespBadRequest(c, err)
		return
	}

	updates, err := core.VmaasAPI.Updates(request)
	if err != nil {
		LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, updates)
}
