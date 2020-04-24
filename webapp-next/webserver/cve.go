package webserver

import (
	"app/cache"
	"app/calc/cves"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func GetCVEs(c *gin.Context) {
	req := cves.Request{
		CveList: []string{c.Param("cve")},
	}

	res, err := cves.CalcCves(cache.C, req)

	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}

func PostCVEs(c *gin.Context) {
	var req cves.Request

	if err := c.ShouldBind(&req); err != nil {
		c.AbortWithStatusJSON(400, ApiError{errors.Wrapf(err, "malformed json").Error()})
		return
	}

	if code, err := req.Validate(); err != nil {
		c.AbortWithStatusJSON(code, ApiError{err.Error()})
		return
	}

	res, err := cves.CalcCves(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}

