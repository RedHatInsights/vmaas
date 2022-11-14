package routes

import (
	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/webapp/controllers"
)

func InitAPI(api *gin.RouterGroup) {
	api.GET("/updates/:package", controllers.UpdatesHandler)
	api.POST("/updates", controllers.UpdatesPostHandler)
	api.GET("/vulnerabilities/:package", controllers.VulnerabilitiesHandler)
	api.POST("/vulnerabilities", controllers.VulnerabilitiesPostHandler)
}
