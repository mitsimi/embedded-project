import type { IClientOptions, MqttClient } from "mqtt";
import mqtt from "mqtt";

class MQTTService {
  private client: MqttClient | null = null;
  private readonly brokerUrl: string;
  private readonly clientId: string;

  constructor(
    brokerUrl: string = `ws://${window.location.hostname}:9001`,
    clientId: string = "web-control-" +
      Math.random().toString(16).substring(2, 10),
  ) {
    this.brokerUrl = brokerUrl;
    this.clientId = clientId;
  }

  async connect(): Promise<void> {
    try {
      return new Promise((resolve, reject) => {
        const options: IClientOptions = {
          clientId: this.clientId,
          clean: true,
        };

        this.client = mqtt.connect(this.brokerUrl, options);

        this.client.on("connect", () => {
          console.log("Connected to MQTT broker");
          resolve();
        });

        this.client.on("error", (err: Error) => {
          console.error("MQTT connection error:", err);
          reject(err);
        });
      });
    } catch (error) {
      console.error("Failed to initialize MQTT client:", error);
      this.client = null;
      throw error;
    }
  }

  disconnect(): void {
    if (this.client) {
      this.client.end();
      this.client = null;
    }
  }

  publishMotorPosition(motorId: number, position: number): void {
    if (!this.client) {
      console.error("MQTT client not connected");
      return;
    }

    const topic = `web/input`;
    const message = `${motorId}:1:${position}`;

    this.client.publish(topic, message, { qos: 1 }, (error?: Error) => {
      if (error) {
        console.error(`Error publishing to ${topic}:`, error);
      }
    });
  }
}

// Create and export a singleton instance
export const mqttService = new MQTTService();
