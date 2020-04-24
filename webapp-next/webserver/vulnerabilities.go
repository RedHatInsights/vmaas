package webserver

import (
	"app/cache"
	"app/calc/vulnerabilities"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func GetVulnerabilities(c *gin.Context) {

	req := vulnerabilities.Request{
		RepoList: []string{},
		Packages: []string{c.Param("nevra")},
	}

	res, err := vulnerabilities.CalcVulnerabilities(cache.C, req)

	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}

func PostVulnerabilities(c *gin.Context) {
	var req vulnerabilities.Request

	if err := c.ShouldBind(&req); err != nil {
		c.AbortWithStatusJSON(400, ApiError{errors.Wrapf(err, "malformed json").Error()})
		return
	}
	if code, err := req.Validate(); err != nil {
		c.AbortWithStatusJSON(code, ApiError{err.Error()})
		return
	}

	res, err := vulnerabilities.CalcVulnerabilities(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}
