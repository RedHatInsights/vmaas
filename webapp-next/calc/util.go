package calc

import (
	"app/cache"
	"github.com/gin-gonic/gin"
)

func DBChange(c *gin.Context) {
	c.JSON(200, cache.C.DbChange)
}
