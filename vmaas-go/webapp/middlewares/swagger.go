package middlewares

import (
	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/docs"

	swaggerFiles "github.com/swaggo/files/v2"
	ginSwagger "github.com/swaggo/gin-swagger"
)

func SetSwagger(app *gin.RouterGroup) {
	// Serving openapi docs
	openapiURL := docs.Init(app)
	basepath := app.BasePath()
	url := ginSwagger.URL(basepath + openapiURL)
	app.GET("/ui/*any", ginSwagger.WrapHandler(swaggerFiles.Handler, url))
}
