package controllers

import (
	"errors"
	"fmt"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas-lib/vmaas"
	"github.com/redhatinsights/vmaas/base/core"
	"github.com/redhatinsights/vmaas/base/utils"
)

func bindValidateJSON(c *gin.Context, request interface{}) error {
	if request == nil {
		return errors.New("nil vmaas request")
	}
	if err := c.BindJSON(request); err != nil {
		errMessage := err.Error()
		if strings.HasPrefix(errMessage, "parsing time") {
			parts := strings.Split(errMessage, `"`)
			var timestamp string
			if len(parts) > 1 {
				timestamp = parts[1]
			}
			return fmt.Errorf("wrong date format (not ISO format with timezone): '%s'", timestamp)
		}
		if strings.HasSuffix(errMessage, "looking for beginning of value") {
			parts := strings.Split(errMessage, ` `)
			var invalidChar string
			if len(parts) > 2 {
				invalidChar = parts[2]
			}
			return fmt.Errorf("malformed input: invalid character '%s'", invalidChar)
		}
		if errMessage == "EOF" {
			return errors.New("request body must not be empty")
		}
		return err
	}

	if reqest, ok := (request).(*vmaas.Request); ok {
		for i, m := range reqest.Modules {
			if m.Module == nil {
				return fmt.Errorf("'module_name' is a required property - 'modules_list.%d'", i)
			}
			if m.Stream == nil {
				return fmt.Errorf("'module_stream' is a required property - 'modules_list.%d'", i)
			}
		}
	}
	return nil
}

func isCacheLoaded(c *gin.Context) bool {
	if core.VmaasAPI == nil || core.VmaasAPI.Cache == nil {
		utils.LogAndRespUnavailable(c, errors.New("data not available, please try again later"))
		return false
	}
	return true
}
