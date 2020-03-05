package webserver

import (
	"app/cache"
	"app/calc/updates"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

type ReportError struct {
	Code  int
	Inner error
}

func (r ReportError) Error() string {
	return r.Inner.Error()
}

type ErrResp struct {
	Error string `json:"error"`
}

func MakeGetUpdates(version int) gin.HandlerFunc {
	includeStrings := version == 1
	supportsNonSec := version >= 3
	secOnly := version < 3

	return func(c *gin.Context) {

		if supportsNonSec {
			secOnly = c.Param("security_only") == "true"
		}

		req := updates.Request{
			RepoList: nil,
			Packages: []string{c.Param("nevra")},
		}

		res, err := updates.Updates(cache.C, req, includeStrings, secOnly)
		if err != nil {
			c.AbortWithStatusJSON(500, ErrResp{err.Error()})
			return
		} else {
			c.JSON(200, res)
		}
	}
}

func MakePostUpdates(version int) gin.HandlerFunc {

	includeStrings := version == 1
	supportsNonSec := version >= 3
	secOnly := version < 3

	return func(c *gin.Context) {
		var req updates.Request

		if supportsNonSec {
			secOnly = c.Param("security_only") == "true"
		}

		err := c.BindJSON(&req)
		if err != nil {
			c.AbortWithStatusJSON(400, ErrResp{errors.Wrapf(err, "malformed json").Error() })
			return
		}

		if code, err := req.Validate(); err != nil {
			c.AbortWithStatusJSON(code, ErrResp{err.Error()})
			return
		}

		res, err := updates.Updates(cache.C, req, includeStrings, secOnly)
		if err != nil {
			c.AbortWithStatusJSON(500, ErrResp{err.Error()})
			return
		} else {
			c.JSON(200, res)
		}
	}
}
