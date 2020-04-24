package webserver

import (
	"app/cache"
	"app/calc/repos"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

func GetRepos(c *gin.Context) {
	req := repos.Request{
		RepoList: []string{c.Param("label")},
	}

	res, err := repos.CalcRepos(cache.C, req)

	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}

func PostRepos(c *gin.Context) {
	var req repos.Request

	if err := c.ShouldBind(&req); err != nil {
		c.AbortWithStatusJSON(400, ApiError{errors.Wrapf(err, "malformed json").Error()})
		return
	}

	if code, err := req.Validate(); err != nil {
		c.AbortWithStatusJSON(code, ApiError{err.Error()})
		return
	}

	res, err := repos.CalcRepos(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, ApiError{err.Error()})
		return
	} else {
		c.JSON(200, res)
	}
}


