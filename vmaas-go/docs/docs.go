package docs

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type openapiData struct {
	filepath string
	url      string
}

var appVersions = map[int]openapiData{
	3: {
		filepath: "./docs/openapi.json",
		url:      "/api/vmaas/v3/openapi.json",
	},
}

func Init(app *gin.Engine) string {
	maxVer := 1
	for ver, data := range appVersions {
		if ver > maxVer {
			maxVer = ver
		}

		app.GET(data.url, getOpenapiHandler(ver))
	}

	return appVersions[maxVer].url
}

func getOpenapiHandler(ver int) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Status(http.StatusOK)
		c.Header("Content-Type", "application/json; charset=utf-8")
		c.File(appVersions[ver].filepath)
	}
}
