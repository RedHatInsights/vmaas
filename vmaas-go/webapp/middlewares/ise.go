package middlewares

import (
	"errors"

	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/base/utils"
)

// respond with predefined 500 error in case of panic
func InternalServerError() gin.RecoveryFunc {
	return func(c *gin.Context, err interface{}) {
		utils.LogAndRespError(c, errors.New("internal server error"))
	}
}

// recover from panic a respond with 500
func Recovery() gin.HandlerFunc {
	return gin.CustomRecovery(InternalServerError())
}
