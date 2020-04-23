package webserver

import (
	"app/calc"
	"app/utils"
	"bytes"
	"github.com/gin-gonic/gin"
	ginprometheus "github.com/zsais/go-gin-prometheus"
	"io"
	"io/ioutil"
	"net/http"
	"net/http/httputil"
	"net/url"
)

type ReportError struct {
	Code  int
	Inner error
}

func (r ReportError) Error() string {
	return r.Inner.Error()
}

type ApiError struct {
	Error string `json:"detail"`
}

type bodyLogWriter struct {
	gin.ResponseWriter
	body *bytes.Buffer
}

func (w bodyLogWriter) Write(b []byte) (int, error) {
	w.body.Write(b)
	return w.ResponseWriter.Write(b)
}

func ProxyCompareMw(c *gin.Context) {
	var proxyBuf bytes.Buffer
	var logBuf bytes.Buffer

	tmpTee := io.TeeReader(c.Request.Body, &proxyBuf)
	tee2 := io.TeeReader(tmpTee, &logBuf)

	// Actual request processing
	c.Request.Body = ioutil.NopCloser(tee2)
	blw := &bodyLogWriter{body: bytes.NewBufferString(""), ResponseWriter: c.Writer}
	c.Writer = blw
	c.Next()

	// Proxy request processing
	destUrl := utils.MustGetEnv("PROXY_ADDRESS") + c.Request.URL.Path
	utils.Log("url", destUrl).Info("Calling")

	proxyReq, err := http.NewRequest(c.Request.Method, destUrl, &proxyBuf)
	if err != nil {
		panic(err)
	}
	proxyReq.Header = c.Request.Header
	resp, err := http.DefaultClient.Do(proxyReq)
	if err != nil {
		panic(err)
	}
	respData, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}

	// Logging for analysis
	utils.Log("path", c.Request.URL.Path, "go", blw.body.String(), "py", string(respData), "req", logBuf.String()).Info("Call")
}

func Proxy(c *gin.Context) {
	utils.Log().Info("Calling proxy")
	remote, err := url.Parse(utils.MustGetEnv("PROXY_ADDRESS"))
	if err != nil {
		panic(err)
	}
	proxy := httputil.NewSingleHostReverseProxy(remote)
	c.Request.URL.Host = remote.Host
	c.Request.Host = remote.Host
	proxy.ServeHTTP(c.Writer, c.Request)
}

func Run() {
	r := gin.Default()
	r.Use(gin.Logger())
	r.RedirectTrailingSlash = true
	r.Use(ProxyCompareMw)
	r.Use(gin.ErrorLogger())
	r.GET("/api/v1/version", func(c *gin.Context) {
		c.String(200, "1.12.2%v", "")
	})
	r.GET("/api/v3/updates/:nevra", MakeGetUpdates(3))
	r.POST("/api/v3/updates", MakePostUpdates(3))

	r.GET("/api/v2/updates/:nevra", MakeGetUpdates(2))
	r.POST("/api/v2/updates", MakePostUpdates(2))

	r.GET("/api/v1/updates/:nevra", MakeGetUpdates(1))
	r.POST("/api/v1/updates", MakePostUpdates(1))

	r.GET("/api/v1/vulnerabilities/:nevra", GetVulnerabilities)
	r.POST("/api/v1/vulnerabilities", PostVulnerabilities)

	r.GET("/api/v1/dbchange", calc.DBChange)

	r.POST("/api/v1/cves", Proxy)
	r.POST("/api/v1/cves/", Proxy)
	//r.GET("/api/v1/cves/:id", Proxy)
	r.GET("/api/v1/cves/*rest", Proxy)

	r.POST("/api/v1/repos", Proxy)
	r.POST("/api/v1/repos/", Proxy)
	//r.GET("/api/v1/repos/:label", Proxy)
	r.GET("/api/v1/repos/*rest", Proxy)

	r.POST("/api/v1/errata", Proxy)
	r.POST("/api/v1/errata/", Proxy)
	//r.GET("/api/v1/errata/:name", Proxy)
	r.GET("/api/v1/errata/*rest", Proxy)

	r.POST("/api/v1/packages", Proxy)
	r.POST("/api/v1/packages/", Proxy)
	//r.GET("/api/v1/packages/:nevra", Proxy)
	r.GET("/api/v1/packages/*rest", Proxy)

	r.POST("/api/v1/pkgtree", Proxy)
	r.POST("/api/v1/pkgtree/", Proxy)
	r.GET("/api/v1/pkgtree/*rest", Proxy)

	r.GET("/metrics", func(c *gin.Context) {
		ginprometheus.NewPrometheus("gin").HandlerFunc()(c)
	})

	r.GET("/api/v1/monitoring/health", func(c *gin.Context) {
		c.Status(200)
	})

	r.Run(":8080")
}
