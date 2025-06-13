package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
)

var (
	mqttBroker   = os.Getenv("MQTT_BROKER")
	mqttTopic1   = os.Getenv("MQTT_TOPIC1")
	mqttTopic2   = os.Getenv("MQTT_TOPIC2")
	influxURL    = os.Getenv("INFLUX_URL")
	influxToken  = os.Getenv("INFLUX_TOKEN")
	influxOrg    = os.Getenv("INFLUX_ORG")
	influxBucket = os.Getenv("INFLUX_BUCKET")
)

var (
	motorPositions = make(map[string]float64)
	mu             sync.RWMutex
)

func main() {
	if mqttBroker == "" || mqttTopic1 == "" || mqttTopic2 == "" ||
		influxURL == "" || influxToken == "" ||
		influxOrg == "" || influxBucket == "" {
		log.Fatalln("Missing env vars. Set MQTT_BROKER, MQTT_TOPIC1, " +
			"MQTT_TOPIC2, INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, " +
			"INFLUX_BUCKET")
	}

	// InfluxDB client
	influxClient := influxdb2.NewClient(influxURL, influxToken)
	writeAPI := influxClient.WriteAPIBlocking(influxOrg, influxBucket)
	defer influxClient.Close()

	// MQTT client options
	opts := mqtt.NewClientOptions().
		AddBroker(mqttBroker).
		SetClientID("motor-collector")
	opts.OnConnect = func(c mqtt.Client) {
		subscribe(c, mqttTopic1, writeAPI)
		subscribe(c, mqttTopic2, writeAPI)
	}

	client := mqtt.NewClient(opts)
	if tok := client.Connect(); tok.Wait() && tok.Error() != nil {
		log.Fatalf("MQTT connect error: %v\n", tok.Error())
	}
	log.Println("Connected to MQTT broker:", mqttBroker)

	// Graceful shutdown
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	<-sigCh

	client.Disconnect(250)
	log.Println("Shutting down")
}

func subscribe(c mqtt.Client, topic string, writeAPI api.WriteAPIBlocking) {
	tok := c.Subscribe(topic, 0, messageHandler(writeAPI))
	tok.Wait()
	if tok.Error() != nil {
		log.Printf("Subscribe error on %s: %v\n", topic, tok.Error())
	} else {
		log.Println("Subscribed to:", topic)
	}
}

func messageHandler(writeAPI api.WriteAPIBlocking) mqtt.MessageHandler {
	return func(_ mqtt.Client, msg mqtt.Message) {
		payload := string(msg.Payload())
		topic := msg.Topic()
		parts := strings.Split(strings.TrimSpace(payload), ":")
		if len(parts) != 3 {
			log.Printf("Invalid format: %s\n", payload)
			return
		}
		motorID := parts[0]
		kind, err := strconv.Atoi(parts[1])
		if err != nil {
			log.Printf("Invalid movement type '%s': %v\n", parts[1], err)
			return
		}
		amt, err := strconv.ParseFloat(parts[2], 64)
		if err != nil {
			log.Printf("Invalid amount '%s': %v\n", parts[2], err)
			return
		}

		mu.Lock()
		cur := motorPositions[motorID]
		var newPos float64
		switch kind {
		case 0: // Absolute
			newPos = amt
		case 1: // Relative
			newPos = cur + amt
		case 2: // Reset
			newPos = 0
		default:
			log.Printf("Unknown movement type '%d'\n", kind)
			mu.Unlock()
			return
		}
		motorPositions[motorID] = newPos
		mu.Unlock()

		p := influxdb2.NewPoint(
			"motor_positions",
			map[string]string{
				"motor_id": motorID,
				"topic":    topic,
			},
			map[string]interface{}{"position": newPos},
			time.Now(),
		)
		if err := writeAPI.WritePoint(context.Background(), p); err != nil {
			log.Printf("InfluxDB write error: %v\n", err)
		} else {
			log.Printf("Wrote motor '%s' pos=%.2f\n", motorID, newPos)
		}
	}
}
