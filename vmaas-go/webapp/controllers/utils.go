package controllers

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/utils"
)

var errorTitles = map[int]string{
	http.StatusInternalServerError: "Internal Server Error",
	http.StatusBadRequest:          "Bad Request",
	http.StatusNotFound:            "Not Found",
	http.StatusMethodNotAllowed:    "Method Not Allowed",
}

func bindValidateJSON(c *gin.Context) (*vmaas.Request, error) {
	request := vmaas.Request{}
	if err := c.BindJSON(&request); err != nil {
		return nil, err
	}
	// validate module name:stream
	for i, m := range request.Modules {
		if len(m.Module) == 0 {
			return nil, fmt.Errorf("'module_stream' is a required property - 'modules_list.%d'", i)
		}
		if len(m.Stream) == 0 {
			return nil, fmt.Errorf("'module_name' is a required property - 'modules_list.%d'", i)
		}
	}
	return &request, nil
}

func respStatusError(c *gin.Context, code int, err error) {
	c.AbortWithStatusJSON(code, utils.ErrorResponse{
		Type:   "about:blank",
		Title:  errorTitles[code],
		Detail: err.Error(),
		Status: code,
	})
}

func LogAndRespError(c *gin.Context, err error) {
	utils.Log("err", err.Error()).Error()
	respStatusError(c, http.StatusInternalServerError, err)
}

func LogAndRespBadRequest(c *gin.Context, err error) {
	utils.Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusBadRequest, err)
}

func LogAndRespNotFound(c *gin.Context, err error) {
	utils.Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusNotFound, err)
}

func LogAndRespNotAllowed(c *gin.Context, err error) {
	utils.Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusMethodNotAllowed, err)
}

func LogAndRespUnavailable(c *gin.Context, err error) {
	utils.Log("err", err.Error()).Warn()
	respStatusError(c, http.StatusServiceUnavailable, err)
}
