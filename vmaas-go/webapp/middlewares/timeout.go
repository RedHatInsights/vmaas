package middlewares

import (
	"errors"
	"time"

	"github.com/redhatinsights/vmaas/base/utils"

	"github.com/gin-contrib/timeout"
	"github.com/gin-gonic/gin"
)

func WithTimeout(duration time.Duration) gin.HandlerFunc {
	return timeout.New(
		timeout.WithTimeout(duration),
		timeout.WithHandler(func(c *gin.Context) {
			c.Next()
		}),
		timeout.WithResponse(func(c *gin.Context) {
			utils.RespGatewayTimeout(c, errors.New("timeout exceeded"))
			c.Done()
		}),
	)
}
