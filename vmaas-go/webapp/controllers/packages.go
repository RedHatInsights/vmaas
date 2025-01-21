package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

func PackagesHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	pkg := c.Param("package")
	req := vmaas.PackagesRequest{Packages: []string{pkg}}

	res, err := core.VmaasAPI.Packages(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)

	// TODO: bump up vmaas-lib version after it's merged:
}

func PackagesPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.PackagesRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	pkgs, err := core.VmaasAPI.Packages(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, pkgs)
}
