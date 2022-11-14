package core

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func Liveness(c *gin.Context) {
	c.JSON(http.StatusOK, "ok")
}

func InitProbes(app *gin.Engine) {
	// public routes
	app.GET("/healthz", Liveness)
}
