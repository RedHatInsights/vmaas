package webapp

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
	"github.com/redhatinsights/vmaas/webapp/middlewares"
	"github.com/redhatinsights/vmaas/webapp/routes"

	_ "net/http/pprof" //nolint:gosec
)

var basepaths = []string{"/api/v1", "/api/vmaas/v1", "/api/v2", "/api/vmaas/v2", "/api/v3", "/api/vmaas/v3"}

//	@title			VMaaS webapp API
//	@version		{{.Version}}
//	@description	API of the VMaaS application on [console.redhat.com](https://console.redhat.com)

//	@license.name	GPLv3
//	@license.url	https://www.gnu.org/licenses/gpl-3.0.en.html

//	@query.collection.format	multi

//	@BasePath	/api/vmaas/v3

func Run() {
	core.ConfigureApp()
	go core.ConfigureCache()

	port := utils.Cfg.PublicPort
	utils.LogInfo(fmt.Sprintf("Webapp starting at port %d", port))
	// create web app
	app := gin.New()

	// middlewares
	app.Use(middlewares.Recovery())
	app.Use(middlewares.RequestResponseLogger())
	middlewares.Prometheus().Use(app)
	app.HandleMethodNotAllowed = true

	// routes
	core.InitProbes(app)
	for _, path := range basepaths {
		api := app.Group(path)
		middlewares.SetSwagger(api)
		routes.InitAPI(api)
	}

	// profiler
	go runProfiler()

	go base.TryExposeOnMetricsPort(app)
	err := utils.RunServer(base.Context, app, port)
	if err != nil {
		utils.LogFatal("err", err.Error(), "server listening failed")
		panic(err)
	}
	utils.LogInfo("webapp completed")
}

// run net/http/pprof on privatePort
func runProfiler() {
	if utils.Cfg.EnableProfiler {
		go func() {
			err := http.ListenAndServe(fmt.Sprintf(":%d", utils.Cfg.PrivatePort), nil) //nolint:gosec
			if err != nil {
				utils.LogWarn("err", err.Error(), "couldn't start profiler")
			}
		}()
	}
}
