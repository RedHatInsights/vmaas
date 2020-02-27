package webserver

import (
	"app/cache"
	"app/calc/updates"
	"github.com/gin-gonic/gin"
)


func SingleUpdate(c *gin.Context) {

	req := updates.Request{
		RepoList: []string{},
		Packages: []string{c.Param("nevra")},
	}

	res, err := updates.Updates(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, err.Error())
	} else {
		c.JSON(200, res)
	}

}

func PostUpdates( c*gin.Context) {
	var req updates.Request

	err := c.BindJSON(&req)
	if err != nil {
		c.AbortWithStatusJSON(500, err.Error())
	}

	res, err := updates.Updates(cache.C, req)
	if err != nil {
		c.AbortWithStatusJSON(500, err.Error())
	} else {
		c.JSON(200, res)
	}
}

