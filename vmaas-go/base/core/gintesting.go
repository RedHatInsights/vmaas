package core

import (
	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/webapp/middlewares"
)

func InitRouter(handler gin.HandlerFunc) *gin.Engine {
	return InitRouterWithParams(handler, "GET", "/")
}

func InitRouterWithParams(handler gin.HandlerFunc, method, path string) *gin.Engine {
	router := gin.Default()
	router.Use(middlewares.RequestResponseLogger())
	router.Handle(method, path, handler)
	return router
}
