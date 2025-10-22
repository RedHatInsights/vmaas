package middlewares

import (
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/redhatinsights/vmaas/base/utils"
	ginprometheus "github.com/zsais/go-gin-prometheus"
)

var requestCount = prometheus.NewCounterVec(prometheus.CounterOpts{
	Help:      "Number of calls per handler",
	Namespace: "vmaas",
	Subsystem: "webapp_go",
	Name:      "handler_invocations",
}, []string{"method", "path", "status"})

var requestTime = prometheus.NewHistogramVec(prometheus.HistogramOpts{
	Help:      "Time spent processing request",
	Namespace: "vmaas",
	Subsystem: "webapp_go",
	Name:      "processing_seconds",
	Buckets:   []float64{1, 1.5, 1.75, 2, 2.5, 3, 3.5, 4},
}, []string{"method", "path"})

// Create and configure Prometheus middleware to expose metrics
func Prometheus() *ginprometheus.Prometheus {
	prometheus.MustRegister(requestCount, requestTime)

	p := ginprometheus.NewPrometheus("vmaas")
	p.MetricsPath = utils.Cfg.MetricsPath
	unifyParametrizedUrlsCounters(p)
	return p
}

func unifyParametrizedUrlsCounters(p *ginprometheus.Prometheus) {
	p.ReqCntURLLabelMappingFn = func(c *gin.Context) string {
		url := c.Request.URL.Path
		for _, p := range c.Params {
			url = strings.Replace(url, "/"+p.Value, "/:"+p.Key, 1)
		}
		if c.Writer.Status() == 404 {
			return "/404"
		}
		return url
	}
}
