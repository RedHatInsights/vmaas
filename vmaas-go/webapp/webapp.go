package webapp

import (
	"io"
	"net/http"

	"github.com/gin-contrib/gzip"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
	"github.com/redhatinsights/vmaas/base"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
	"github.com/redhatinsights/vmaas/webapp/controllers"
	"github.com/redhatinsights/vmaas/webapp/middlewares"
	"github.com/redhatinsights/vmaas/webapp/routes"
)

var basepaths = []string{"/api/v3", "/api/vmaas/v3"}

// nolint: lll
// @title VMaaS webapp API
// @version  {{.Version}}
// @description API of the VMaaS application on [console.redhat.com](https://console.redhat.com)

// @license.name GPLv3
// @license.url https://www.gnu.org/licenses/gpl-3.0.en.html

// @query.collection.format multi

// @BasePath /api/vmaas/v3
func Run() {
	core.ConfigureApp()
	go core.ConfigureCache()

	port := utils.Cfg.PublicPort
	utils.Log().Infof("Webapp starting at port %d", port)
	// create web app
	app := gin.New()

	// middlewares
	app.Use(middlewares.RequestResponseLogger())
	app.Use(gzip.Gzip(gzip.DefaultCompression))
	app.HandleMethodNotAllowed = true

	// routes
	core.InitProbes(app)
	app.NoRoute(vmaasProxy)
	for _, path := range basepaths {
		api := app.Group(path)
		routes.InitAPI(api)
	}

	go base.TryExposeOnMetricsPort(app)

	err := utils.RunServer(base.Context, app, port)
	if err != nil {
		utils.Log("err", err.Error()).Fatal("server listening failed")
		panic(err)
	}
	utils.Log().Info("webapp completed")
}

func vmaasProxy(c *gin.Context) {
	c.Request.RequestURI = ""
	c.Request.URL.Scheme = "http"
	c.Request.URL.Host = utils.Cfg.OGWebappHost
	res, err := http.DefaultClient.Do(c.Request)
	if err != nil {
		controllers.LogAndRespFailedDependency(c, errors.Wrap(err, "error making http request"))
		return
	}

	resBody, err := io.ReadAll(res.Body)
	if err != nil {
		controllers.LogAndRespFailedDependency(c, errors.Wrap(err, "could not read response body"))
		return
	}
	c.Data(res.StatusCode, res.Header.Get("Content-Type"), resBody)
}
