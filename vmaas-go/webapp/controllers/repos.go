package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// ReposHandler godoc
//
//	@Summary		Get details for a repository
//	@Description	Get details about a repository.
//	@Description	It is possible to use a POSIX regular expression as a pattern for repository names.
//	@Produce		json
//	@Param			repo	path	string	true	"repository"
//	@Success		200	{object}	vmaas.Repos
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/repos/{repo} [get]
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

// ReposPostHandler godoc
//
//	@Summary		Get details for repositories
//	@Description	Get details about repositories. Use `repository_list` parameter to provide a list of repository names, or a single POSIX regular expression.
//	@Accept			json
//	@Produce		json
//	@Param			repository_list	body	vmaas.ReposRequest	true	"repository_list"
//	@Success		200	{object}	vmaas.Repos
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/repos [post]
//
//nolint:lll
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
