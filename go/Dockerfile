FROM golang:1.22-alpine AS builder

WORKDIR /app/go

# Copy go.mod and go.sum to cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the code
COPY /go .

# Build the Go application
RUN go build -o main ./go/cmd/main.go

# Run the application
CMD ["./main"]
