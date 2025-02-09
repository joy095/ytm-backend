package routes

import (
	"backend/routes/handlers" // Import the handlers package

	"github.com/gin-gonic/gin"
)

// RegisterRoutes registers all the routes for the application.
func RegisterRoutes(router *gin.Engine) {
	router.POST("/verify", handlers.VerifyTokenHandler)
}
