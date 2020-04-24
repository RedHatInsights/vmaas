package webserver

import (
	"app/cache"
	"app/calc/packages"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func GetPackages(c *gin.Context) {
	req := packages.Request{
		PackageList: []string{c.Param("pkg")},
	}

	res, err := packages.CalcPackages(cache.C, req)

	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}

func PostPackages(c *gin.Context) {
	var req packages.Request

	if err := c.ShouldBind(&req); err != nil {
		c.AbortWithStatusJSON(400, ApiError{errors.Wrapf(err, "malformed json").Error()})
		return
	}

	if code, err := req.Validate(); err != nil {
		c.AbortWithStatusJSON(code, ApiError{err.Error()})
		return
	}

	res, err := packages.CalcPackages(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}
