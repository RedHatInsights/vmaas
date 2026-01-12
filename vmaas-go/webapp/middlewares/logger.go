package middlewares

import (
	"net/http"
	"strconv"
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
		// Calculate exact size: 14 fixed fields + 1 ("request") + 2 per param
		capacity := 15 + (len(c.Params) * 2)
		fields := make([]interface{}, 0, capacity)

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
			utils.LogInfo(append(fields, "request")...)
		} else {
			utils.LogError(append(fields, "request")...)
		}

		utils.ObserveSecondsSince(tStart, requestTime.WithLabelValues(c.Request.Method, c.FullPath()))
		requestCount.WithLabelValues(c.Request.Method, c.FullPath(), strconv.Itoa(c.Writer.Status())).Inc()
	}
}
