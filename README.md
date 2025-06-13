# Robotic Arm Control System

> [!NOTE]
> This project is part of the "Embedded Systems" university course.

## Project Overview

This project implements a robotic arm control system with multiple components that communicate via MQTT, enabling modular development and operation.

## System Components

### 1. Web Interface (`/web`)

A browser-based user interface that provides:

- Real-time camera feed display
- Robotic arm control interface

A python backend which serves:

- Raspberry Pi camera or webcam feed

### 2. Game Controller Interface (`/controller`)

Enables control of the robotic arm using a game controller:

- Controller input processing
- Command translation
- MQTT message publishing

### 3. Motor Control System (`/motorController`)

The embedded system responsible for:

- Command execution
- Position tracking
- Motor movement control

### 4. Datastore (`/metrics`)

A little service written in Go which ingests MQTT messages in the database.

### 5. Mosquitto Broker (`/mosquitto`)

MQTT broker configuration and setup with Docker:

- Broker settings
- Security configuration
- Network setup
