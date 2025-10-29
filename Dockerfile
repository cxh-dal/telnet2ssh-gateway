# syntax=docker/dockerfile:1

FROM --platform=$BUILDPLATFORM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod ./
COPY go.sum ./
RUN go mod download
COPY . .
ARG TARGETOS
ARG TARGETARCH
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -trimpath -ldflags "-s -w" -o /out/tts-proxy ./cmd/tts-proxy

FROM alpine:3.20
WORKDIR /app
RUN adduser -D -u 10001 appuser && mkdir -p /data && chown -R appuser /data
COPY --from=builder /out/tts-proxy /app/tts-proxy
USER appuser
ENV CONFIG_PATH=/data/config.json \
    HOST_KEY_PATH=/data/ssh_host_rsa_key \
    HEALTH_ADDR=:8080 \
    SSH_USERNAME=ritts \
    SSH_PASSWORD=ritts
EXPOSE 4001-4032/tcp 8080/tcp
VOLUME ["/data"]
ENTRYPOINT ["/app/tts-proxy","serve"]
