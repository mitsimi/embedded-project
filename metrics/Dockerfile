FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY go.mod ./
COPY main.go ./
RUN go mod tidy
RUN go build -o metrics-collector

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/metrics-collector .
ENV MQTT_BROKER=""
ENV MQTT_TOPIC1=""
ENV MQTT_TOPIC2=""
ENV INFLUX_URL=""
ENV INFLUX_TOKEN=""
ENV INFLUX_ORG=""
ENV INFLUX_BUCKET=""
CMD ["./metrics-collector"]