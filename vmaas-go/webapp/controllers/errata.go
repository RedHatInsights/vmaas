package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

// ErrataHandler godoc
//
//	@Summary		Get details for an erratum
//	@Description	Get details about an erratum. It is possible to use a POSIX regular expression as a pattern for errata names.
//	@Produce		json
//	@Param			erratum	path	string	true	"erratum"
//	@Success		200	{object}	vmaas.Errata
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/errata/{erratum} [get]
//
//nolint:lll
func ErrataHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	erratum := c.Param("erratum")
	req := vmaas.ErrataRequest{Errata: []string{erratum}}

	res, err := core.VmaasAPI.Errata(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, res)
}

// ErrataPostHandler godoc
//
//	@Summary		Get details for errata
//	@Description	Get details about errata with additional parameters. Use `errata_list` parameter to provide a list of errata names, or a single POSIX regular expression.
//	@Accept			json
//	@Produce		json
//	@Param			errata_list	body	vmaas.ErrataRequest	true	"errata_list"
//	@Success		200	{object}	vmaas.Errata
//	@Failure		400	{object}	utils.ErrorResponse
//	@Failure		424	{object}	utils.ErrorResponse
//	@Failure		500	{object}	utils.ErrorResponse
//	@Failure		503	{object}	utils.ErrorResponse
//	@Router			/errata [post]
//
//nolint:lll
func ErrataPostHandler(c *gin.Context) {
	if !isCacheLoaded(c) {
		return
	}
	req := vmaas.ErrataRequest{}
	err := bindValidateJSON(c, &req)
	if err != nil {
		utils.LogAndRespBadRequest(c, err)
		return
	}

	errata, err := core.VmaasAPI.Errata(&req)
	if err != nil {
		utils.LogAndRespError(c, err)
		return
	}
	c.JSON(http.StatusOK, errata)
}
