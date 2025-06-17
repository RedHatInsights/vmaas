package middlewares

import (
	"github.com/gin-gonic/gin"
	"github.com/redhatinsights/vmaas/docs"

	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

func SetSwagger(app *gin.Engine) {
	// Serving openapi docs
	openapiURL := docs.Init(app)
	url := ginSwagger.URL(openapiURL)
	app.GET("/openapi/*any", ginSwagger.WrapHandler(swaggerFiles.Handler, url))
}
