package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

func ReposHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	repo := c.Param("repo")
	req := vmaas.ReposRequest{Repos: []string{repo}}

	res, err := core.VmaasAPI.Repos(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

func ReposPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.ReposRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	res, err := core.VmaasAPI.Repos(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}
