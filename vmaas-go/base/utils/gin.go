package utils

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
)

// ReadHeaderTimeout same as nginx default
const ReadHeaderTimeout = 60 * time.Second

type ErrorResponse struct {
	Type   string `json:"type"`
	Title  string `json:"title"`
	Detail string `json:"detail"`
	Status int    `json:"status"`
}

var errorTitles = map[int]string{
	http.StatusInternalServerError: "Internal Server Error",
	http.StatusBadRequest:          "Bad Request",
	http.StatusNotFound:            "Not Found",
	http.StatusMethodNotAllowed:    "Method Not Allowed",
}

func LoadParamInt(c *gin.Context, param string, defaultValue int, query bool) (int, error) {
	var valueStr string
	if query {
		valueStr = c.Query(param)
	} else {
		valueStr = c.Param(param)
	}
	if valueStr == "" {
		return defaultValue, nil
	}

	value, err := strconv.Atoi(valueStr)
	if err != nil {
		return 0, err
	}

	return value, nil
}

func LoadLimitOffset(c *gin.Context, defaultLimit int) (int, int, error) {
	offset, err := LoadParamInt(c, "offset", 0, true)
	if err != nil {
		return 0, 0, err
	}

	limit, err := LoadParamInt(c, "limit", defaultLimit, true)
	if err != nil {
		return 0, 0, err
	}

	if err := CheckLimitOffset(limit, offset); err != nil {
		return 0, 0, err
	}

	return limit, offset, nil
}

func CheckLimitOffset(limit int, offset int) error {
	if offset < 0 {
		return errors.New("offset must not be negative")
	}
	if limit < 1 && limit != -1 {
		return errors.New("limit must not be less than 1, or should be -1 to return all items")
	}
	return nil
}

func RunServer(ctx context.Context, handler http.Handler, port int) error {
	addr := fmt.Sprintf(":%d", port)
	srv := http.Server{Addr: addr, Handler: handler, ReadHeaderTimeout: ReadHeaderTimeout, MaxHeaderBytes: 65535}
	go func() {
		<-ctx.Done()
		err := srv.Shutdown(context.Background())
		if err != nil {
			Log("err", err.Error()).Error("server shutting down failed")
			return
		}
		Log().Info("server closed successfully")
	}()

	err := srv.ListenAndServe()
	if err != nil && err != http.ErrServerClosed {
		return errors.Wrap(err, "server listening failed")
	}
	return nil
}

func respStatusError(c *gin.Context, code int, err error) {
	c.AbortWithStatusJSON(code, ErrorResponse{
		Type:   "about:blank",
		Title:  errorTitles[code],
		Detail: err.Error(),
		Status: code,
	})
}

func LogAndRespError(c *gin.Context, err error) {
	Log("err", err.Error()).Error()
	respStatusError(c, http.StatusInternalServerError, err)
}

func LogAndRespBadRequest(c *gin.Context, err error) {
	Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusBadRequest, err)
}

func LogAndRespNotFound(c *gin.Context, err error) {
	Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusNotFound, err)
}

func LogAndRespNotAllowed(c *gin.Context, err error) {
	Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusMethodNotAllowed, err)
}

func LogAndRespUnavailable(c *gin.Context, err error) {
	Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusServiceUnavailable, err)
}

func LogAndRespFailedDependency(c *gin.Context, err error) {
	Log("err", err.Error()).Error() // log more descriptive error, possibly showing internal urls
	respStatusError(c, http.StatusFailedDependency, errors.New("couldn't proxy request to vmaas-webapp-service"))
}
