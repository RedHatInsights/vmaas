package reposcan_data_server

import (
	"net/http"
	"time"

	"github.com/redhatinsights/vmaas/base"
	"github.com/redhatinsights/vmaas/base/utils"
)

const dataDir = "/data"

// responseWriter wraps http.ResponseWriter to capture status code and bytes written.
type responseWriter struct {
	http.ResponseWriter
	status int
	bytes  int
}

func (rw *responseWriter) WriteHeader(status int) {
	rw.status = status
	rw.ResponseWriter.WriteHeader(status)
}

func (rw *responseWriter) Write(b []byte) (int, error) {
	n, err := rw.ResponseWriter.Write(b)
	rw.bytes += n
	return n, err
}

// loggingMiddleware logs each request with method, path, status, bytes, and duration.
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tStart := time.Now()
		rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(rw, r)
		durationMs := time.Since(tStart).Milliseconds()
		logFn := utils.LogInfo
		if rw.status >= http.StatusInternalServerError {
			logFn = utils.LogError
		}
		logFn(
			"durationMs", durationMs,
			"status_code", rw.status,
			"method", r.Method,
			"url", r.URL.String(),
			"bytes", rw.bytes,
			"request",
		)
	})
}

func Run() {
	utils.ConfigureConfig()
	utils.ConfigureLogging()
	p := utils.Cfg.PrivatePort
	utils.LogInfo("port", p, "data_dir", dataDir, "reposcan-data-server starting")

	handler := loggingMiddleware(http.FileServer(http.Dir(dataDir)))
	err := utils.RunServer(base.Context, handler, p)
	if err != nil {
		utils.LogFatal("err", err.Error(), "reposcan-data-server failed")
	}
	utils.LogInfo("reposcan-data-server completed")
}
