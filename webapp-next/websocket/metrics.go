package websocket

import (
	"github.com/prometheus/client_golang/prometheus"
)

var (
	RequestTime = prometheus.NewHistogramVec(prometheus.HistogramOpts{
		Namespace: "vmaas",
		Subsystem: "webapp",
		Name:      "processing_seconds",
	}, []string{"method", "path"})

)
func init() {
	prometheus.MustRegister(RequestTime)
}