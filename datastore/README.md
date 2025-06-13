# Motor Metrics Collector

This service collects and stores motor position data from MQTT topics into InfluxDB. It subscribes to two MQTT topics (`web/input` and `controller/input`) and processes messages containing motor movement data.

## Features

- Subscribes to MQTT topics for motor position updates
- Processes three types of movements:
  - Absolute position (type 0)
  - Relative position (type 1)
  - Reset position (type 2)
- Stores motor positions in InfluxDB for time-series analysis
- Supports multiple motors with unique IDs

## Prerequisites

- Docker and Docker Compose
- MQTT broker running on localhost:1883

## Quick Start

1. Clone this repository
2. Start the service using Docker Compose:
   ```bash
   docker compose up -d
   ```

The service will start two containers:

- InfluxDB (accessible at http://localhost:8086)
- Metrics Collector (connects to MQTT and InfluxDB)

## Configuration

The service is configured through environment variables in `compose.yml`:

- `MQTT_BROKER`: MQTT broker address (default: tcp://127.0.0.1:1883)
- `MQTT_TOPIC1`: First MQTT topic to subscribe to (default: web/input)
- `MQTT_TOPIC2`: Second MQTT topic to subscribe to (default: controller/input)
- `INFLUX_URL`: InfluxDB URL (default: http://127.0.0.1:8086)
- `INFLUX_TOKEN`: InfluxDB authentication token
- `INFLUX_ORG`: InfluxDB organization name
- `INFLUX_BUCKET`: InfluxDB bucket name

## Message Format

The service expects MQTT messages in the following format:

```
motor_id:movement_type:amount
```

Where:

- `motor_id`: Unique identifier for the motor
- `movement_type`: 0 (absolute), 1 (relative), or 2 (reset)
- `amount`: Position value (float)

Example: `motor1:1:10.5` (move motor1 10.5 units relative to current position)

## Data Storage

Motor positions are stored in InfluxDB with the following structure:

- Measurement: `motor_positions`
- Tags: `motor_id`, `topic`
- Fields: `position`
- Timestamp: Automatically added
