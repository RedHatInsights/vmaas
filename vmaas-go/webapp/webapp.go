package webapp

import (
	"fmt"
	"io"
	"net/http"
	"net/url"

	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
	"github.com/redhatinsights/vmaas/base"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
	"github.com/redhatinsights/vmaas/webapp/middlewares"
	"github.com/redhatinsights/vmaas/webapp/routes"

	_ "net/http/pprof" //nolint:gosec
)

var basepaths = []string{"/api/v3", "/api/vmaas/v3"}

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
	app.NoRoute(vmaasProxy)
	for _, path := range basepaths {
		api := app.Group(path)
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

func vmaasProxy(c *gin.Context) {
	u, err := url.Parse(utils.Cfg.OGWebappAddress)
	if err != nil {
		panic(err)
	}
	c.Request.RequestURI = ""
	c.Request.URL.Scheme = u.Scheme
	c.Request.URL.Host = u.Host
	res, err := http.DefaultClient.Do(c.Request)
	if err != nil {
		utils.LogAndRespFailedDependency(c, errors.Wrap(err, "error making http request"))
		return
	}
	defer res.Body.Close()

	resBody, err := io.ReadAll(res.Body)
	if err != nil {
		utils.LogAndRespFailedDependency(c, errors.Wrap(err, "could not read response body"))
		return
	}
	c.Header("Content-Encoding", res.Header.Get("Content-Encoding"))
	c.Data(res.StatusCode, res.Header.Get("Content-Type"), resBody)
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
