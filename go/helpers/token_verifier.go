package helpers

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"google.golang.org/api/idtoken"
)

var googleClientID = os.Getenv("GOOGLE_CLIENT_ID")

func VerifyGoogleIDToken(idToken string) (*idtoken.Payload, error) {
	// Decode token to check expiration
	if isTokenExpired(idToken) {
		return nil, fmt.Errorf("token has expired")
	}

	ctx := context.Background()
	validator, err := idtoken.NewValidator(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to create token validator: %w", err)
	}

	payload, err := validator.Validate(ctx, idToken, googleClientID)
	if err != nil {
		return nil, fmt.Errorf("failed to validate token: %w", err)
	}

	return payload, nil
}

func isTokenExpired(idToken string) bool {
	segments := splitToken(idToken)
	if len(segments) != 3 {
		return true // Invalid token structure
	}

	decoded, err := base64.RawURLEncoding.DecodeString(segments[1])
	if err != nil {
		return true
	}

	var claims map[string]interface{}
	if err := json.Unmarshal(decoded, &claims); err != nil {
		return true
	}

	if exp, ok := claims["exp"].(float64); ok {
		return time.Now().Unix() > int64(exp)
	}

	return true
}

func splitToken(idToken string) []string {
	return strings.Split(idToken, ".")
}
