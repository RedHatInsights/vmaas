package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

func VulnerabilitiesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	pkg := c.Param("package")
	request := vmaas.Request{Packages: []string{pkg}, UseCsaf: true}

	vulnerabilities, err := core.VmaasAPI.Vulnerabilities(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, vulnerabilities)
}

func VulnerabilitiesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	request := vmaas.Request{UseCsaf: true}
	err := bindValidateJSON(c, &request)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	if request.Extended {
		vulnerabilities, err := core.VmaasAPI.VulnerabilitiesExtended(&request)
		if err != nil {
			utils.LogAndRespError(c, err)
			return
		}
		c.JSON(http.StatusOK, vulnerabilities)
		return
	}

	vulnerabilities, err := core.VmaasAPI.Vulnerabilities(&request)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, vulnerabilities)
}
