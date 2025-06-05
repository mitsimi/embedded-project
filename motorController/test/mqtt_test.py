import paho.mqtt.client as mqtt

SUBSCRIBE_TOPIC = "motor_movement"

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.publish(SUBSCRIBE_TOPIC, "6:0:200")
client.publish(SUBSCRIBE_TOPIC, "6:1:4100")
client.publish(SUBSCRIBE_TOPIC, "6:4:20230")