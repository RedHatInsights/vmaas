package routes

import (
	"github.com/gin-contrib/gzip"
	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/utils"
	"github.com/redhatinsights/vmaas/webapp/controllers"
)

func InitAPI(api *gin.RouterGroup) {
	api.Use(gzip.Gzip(gzip.DefaultCompression))
	api.GET("/updates/:package", controllers.UpdatesHandler)
	api.POST("/updates", controllers.UpdatesPostHandler)
	api.GET("/vulnerabilities/:package", controllers.VulnerabilitiesHandler)
	api.POST("/vulnerabilities", controllers.VulnerabilitiesPostHandler)

	if utils.Cfg.EnableGoCves {
		api.GET("/cves/:cve", controllers.CvesHandler)
		api.POST("/cves", controllers.CvesPostHandler)
	}
}
