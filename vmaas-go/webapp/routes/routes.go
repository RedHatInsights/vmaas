package routes

import (
	"github.com/gin-contrib/gzip"
	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/webapp/controllers"
)

func InitAPI(api *gin.RouterGroup) {
	api.Use(gzip.Gzip(gzip.DefaultCompression))
	api.GET("/updates/:package", controllers.UpdatesHandler)
	api.POST("/updates", controllers.UpdatesPostHandler)
	api.GET("/vulnerabilities/:package", controllers.VulnerabilitiesHandler)
	api.POST("/vulnerabilities", controllers.VulnerabilitiesPostHandler)

	api.GET("/cves/:cve", controllers.CvesHandler)
	api.POST("/cves", controllers.CvesPostHandler)

	api.GET("/errata/:erratum", controllers.ErrataHandler)
	api.POST("/errata", controllers.ErrataPostHandler)

	api.GET("/repos/:repo", controllers.ReposHandler)
	api.POST("/repos", controllers.ReposPostHandler)

	api.GET("/packages/:nevra", controllers.PackagesHandler)
	api.POST("/packages", controllers.PackagesPostHandler)

	api.POST("/pkglist", controllers.PkgListPostHandler)

	api.GET("/pkgtree/:package_name", controllers.PkgTreeHandler)
	api.POST("/pkgtree", controllers.PkgTreePostHandler)

	api.GET("/patches/:nevra", controllers.PatchesHandler)
	api.POST("/patches", controllers.PatchesPostHandler)

	api.GET("/package_names/rpms/:rpm", controllers.RPMPkgNamesHandler)
	api.POST("/package_names/rpms", controllers.RPMPkgNamesPostHandler)

	api.GET("/package_names/srpms/:srpm", controllers.SRPMPkgNamesHandler)
	api.POST("/package_names/srpms", controllers.SRPMPkgNamesPostHandler)

	api.GET("/dbchange", controllers.DBChangeHandler)

	api.GET("/version", controllers.VersionHandler)

	api.GET("/os/vulnerability/report", controllers.OSHandler)
}
