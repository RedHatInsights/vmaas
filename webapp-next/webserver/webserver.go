package webserver

import (
	"github.com/gin-gonic/gin"
	"net/http/httputil"
	"net/url"
)


func Proxy(c *gin.Context) {
	remote, err := url.Parse("http://vmaas_webapp:8080")
	if err != nil {
		panic(err)
	}
	proxy := httputil.NewSingleHostReverseProxy(remote)
	c.Request.Host = remote.Host
	proxy.ServeHTTP(c.Writer, c.Request)
}

func Run() {
	r := gin.Default()

	r.GET("/api/v3/updates/:nevra", SingleUpdate)
	r.POST("/api/v3/updates", PostUpdates)

	r.GET("/api/v1/dbchange", Proxy)
	
	r.GET("/api/v2/updates/:nevra", Proxy)
	r.POST("/api/v2/updates", Proxy)


	r.GET("/api/v1/updates/:nevra", Proxy)
	r.POST("/api/v1/updates", Proxy)

	r.POST("/api/v1/cves", Proxy)
	r.GET("/api/v1/cves/:id", Proxy)

	r.POST("/api/v1/repos", Proxy)
	r.GET("/api/v1/repos/:label", Proxy)

	r.POST("/api/v1/errata", Proxy)
	r.GET("/api/v1/errata/:name", Proxy)

	r.POST("/api/v1/packages", Proxy)
	r.GET("/api/v1/packages/:nevra", Proxy)

	r.POST("/api/v1/vulnerabilities", Proxy)
	r.GET("/api/v1/vulnerabilities/:nevra", Proxy)

	r.Run(":1080")
}
