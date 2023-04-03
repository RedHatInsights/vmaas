package controllers

import (
	"errors"
	"fmt"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

func bindValidateJSON(c *gin.Context) (*vmaas.Request, error) {
	request := vmaas.Request{}
	if err := c.BindJSON(&request); err != nil {
		return nil, err
	}
	// validate module name:stream
	for i, m := range request.Modules {
		if m.Module == nil {
			return nil, fmt.Errorf("'module_name' is a required property - 'modules_list.%d'", i)
		}
		if m.Stream == nil {
			return nil, fmt.Errorf("'module_stream' is a required property - 'modules_list.%d'", i)
		}
	}
	return &request, nil
}

func isCacheLoaded(c *gin.Context) bool {
	if core.VmaasAPI == nil || core.VmaasAPI.Cache == nil {
		utils.LogAndRespUnavailable(c, errors.New("data not available, please try again later"))
		return false
	}
	return true
}
