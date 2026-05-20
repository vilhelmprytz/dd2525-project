FROM golang:1.26-alpine
WORKDIR /app
RUN go install github.com/google/capslock/cmd/capslock@latest
RUN apk --no-cache add git
CMD ["/bin/ash"]
