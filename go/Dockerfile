# Build stage
FROM golang:1.22-alpine as builder

WORKDIR /app

# Cache dependencies layer
COPY go.mod go.sum ./
RUN go mod download

# Build with optimizations for size
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags='-w -s' \
    -o gin-service \
    ./cmd/main.go

# Runtime stage
FROM alpine:latest
WORKDIR /app

# Copy only the compiled binary
COPY --from=builder /app/gin-service .

EXPOSE 8080

ENTRYPOINT ["./gin-service"]