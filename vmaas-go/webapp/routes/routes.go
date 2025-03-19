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
	if utils.Cfg.EnableGoErrata {
		api.GET("/errata/:erratum", controllers.ErrataHandler)
		api.POST("/errata", controllers.ErrataPostHandler)
	}
	if utils.Cfg.EnableGoRepos {
		api.GET("/repos/:repo", controllers.ReposHandler)
		api.POST("/repos", controllers.ReposPostHandler)
	}
	if utils.Cfg.EnableGoPackages {
		api.GET("/packages/:nevra", controllers.PackagesHandler)
		api.POST("/packages", controllers.PackagesPostHandler)
	}
	if utils.Cfg.EnableGoPkgList {
		api.POST("/pkglist", controllers.PkgListPostHandler)
	}
	if utils.Cfg.EnableGoPkgTree {
		api.GET("/pkgtree/:package_name", controllers.PkgTreeHandler)
		api.POST("/pkgtree", controllers.PkgTreePostHandler)
	}
	if utils.Cfg.EnableGoPatches {
		api.GET("/patches/:nevra", controllers.PatchesHandler)
		api.POST("/patches", controllers.PatchesPostHandler)
	}
	if utils.Cfg.EnableGoRPMPkgNames {
		api.GET("/package_names/rpms/:rpm", controllers.RPMPkgNamesHandler)
		api.POST("/package_names/rpms", controllers.RPMPkgNamesPostHandler)
	}
	if utils.Cfg.EnableGoSRPMPkgNames {
		api.GET("/package_names/srpms/:srpm", controllers.SRPMPkgNamesHandler)
		api.POST("/package_names/srpms", controllers.SRPMPkgNamesPostHandler)
	}
	if utils.Cfg.EnableGoDBChange {
		api.GET("/dbchange", controllers.DBChangeHandler)
	}
	if utils.Cfg.EnableGoVersion {
		api.GET("/version", controllers.VersionHandler)
	}
	api.GET("/os/vulnerability/report", controllers.OSHandler)
}
