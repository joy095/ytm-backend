package handlers

import (
	"backend/helpers"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

func VerifyTokenHandler(c *gin.Context) {
	authHeader := c.GetHeader("Authorization")
	if authHeader == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header missing"})
		return
	}

	token := extractToken(authHeader)
	if token == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Token missing"})
		return
	}

	payload, err := helpers.VerifyGoogleIDToken(token)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token", "details": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"email": payload.Claims["email"],
		"name":  payload.Claims["name"],
	})
}

func extractToken(authHeader string) string {
	return strings.Replace(authHeader, "Bearer ", "", 1)
}
