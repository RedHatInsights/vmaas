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

	//upda(cache.C, req, includeStrings, supportsNonSec && !requestedSecOnly)
	if err != nil {
		c.AbortWithStatusJSON(500, err.Error())
		return
	} else {
		c.JSON(200, res)
	}
}

func PostVulnerabilities(c *gin.Context) {
	var req vulnerabilities.Request

	err := c.BindJSON(&req)
	if err != nil {
		c.AbortWithStatusJSON(500, err.Error())
		return
	}

	res, err := vulnerabilities.CalcVulnerabilities(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, err.Error())
		return
	} else {
		c.JSON(200, res)
	}
}
