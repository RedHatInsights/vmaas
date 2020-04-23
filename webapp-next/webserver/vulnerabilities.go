package webserver

import (
	"app/cache"
	"app/calc/vulnerabilities"
	"github.com/gin-gonic/gin"
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

	if err := c.ShouldBindJSON(&req); err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
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
