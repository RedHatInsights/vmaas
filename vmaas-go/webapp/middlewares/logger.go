package middlewares

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/utils"
)

// setup logging middleware
// ensures logging line after each http response with fields:
// duration_ms, status, userAgent, method, remoteAddr, url, param_*
func RequestResponseLogger() gin.HandlerFunc {
	return func(c *gin.Context) {
		tStart := time.Now()
		c.Next()
		var fields []interface{}

		duration := time.Since(tStart).Nanoseconds() / 1e6
		fields = append(fields, "durationMs", duration,
			"status_code", c.Writer.Status(),
			"user_agent", c.Request.UserAgent(),
			"method", c.Request.Method,
			"remote_addr", c.Request.RemoteAddr,
			"url", c.Request.URL.String(),
			"content_encoding", c.Writer.Header().Get("Content-Encoding"))

		for _, param := range c.Params {
			fields = append(fields, "param_"+param.Key, param.Value)
		}

		if c.Writer.Status() < http.StatusInternalServerError {
			utils.Log(fields...).Info("request")
		} else {
			utils.Log(fields...).Error("request")
		}

		// FIXME: prometheus
		// utils.ObserveSecondsSince(tStart, requestDurations.WithLabelValues(c.Request.Method+c.Request.URL.String()))
	}
}
