package webserver

import (
	"app/cache"
	"app/calc/errata"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func GetErrata(c *gin.Context) {
	req := errata.Request{
		ErrataList: []string{c.Param("erratum")},
	}

	res, err := errata.CalcErrata(cache.C, req)

	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}

func PostErrata(c *gin.Context) {
	var req errata.Request

	if err := c.ShouldBind(&req); err != nil {
		c.AbortWithStatusJSON(400, ApiError{errors.Wrapf(err, "malformed json").Error()})
		return
	}

	if code, err := req.Validate(); err != nil {
		c.AbortWithStatusJSON(code, ApiError{err.Error()})
		return
	}

	res, err := errata.CalcErrata(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}
