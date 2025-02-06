FROM golang:1.22-alpine AS go-builder

WORKDIR /app

# Copy go.mod and go.sum (relative to the Docker build context)
COPY ./go.mod ./go.sum ./

# Download dependencies
RUN go mod download

# Copy the rest of the Go project
COPY ./ ./

# Build the Gin service from cmd/main.go
RUN go build -o gin-service ./cmd/main.go

# Use a minimal final image
FROM alpine:latest
WORKDIR /root/
COPY --from=go-builder /app/gin-service .

EXPOSE 8080
ENTRYPOINT ["./gin-service"]
