import paho.mqtt.client as mqtt
from inputs import get_gamepad

broker = "mqtt.eclipseprojects.io"
topic = "controller/input"

client = mqtt.Client()
client.connect(broker, 1883, 60)

channel_ranges = {
    0: (100, 380),  # Gripper
    1: (100, 500),  # Gripper Arm
    2: (100, 470),  # Upper Arm
    3: (100, 520),  # Middle Arm
    4: (220, 480)  # Lower Arm
}

def scale_value(value, min_value, max_value):
    return int(min_value + (max_value - min_value) * ((value + 32768) / 65536))  # Annahme: Wertebereich des Controllers [-32768, 32767]

print("Drücke einen Knopf..")

while True:
    events = get_gamepad()
    for event in events:
        if event.ev_type == "Absolute":  # Achsenbewegung
            channel = None
            pulse = None
            
            if event.code == "ABS_X":  # Beispiel: Steuerung für Gripper
                channel = 0
                pulse = scale_value(event.state, *channel_ranges[channel])
            elif event.code == "ABS_Y":  # Beispiel: Steuerung für Gripper Arm
                channel = 1
                pulse = scale_value(event.state, *channel_ranges[channel])
            elif event.code == "ABS_RX":  # Beispiel: Steuerung für Upper Arm
                channel = 2
                pulse = scale_value(event.state, *channel_ranges[channel])
            elif event.code == "ABS_RY":  # Beispiel: Steuerung für Middle Arm
                channel = 3
                pulse = scale_value(event.state, *channel_ranges[channel])

            if channel is not None and pulse is not None:
                message = f"{channel}:0:{pulse}"  # "0" = absolute Bewegung
                client.publish(topic, message)
                print(f"Nachricht gesendet: {message}")

        elif event.ev_type == "Key" and event.state == 1:  # Taste gedrückt
            if event.code == "BTN_SOUTH":  # Beispiel für Move-Typ 2 (Reset)
                message = "2"  # Alle Motoren zurücksetzen
                client.publish(topic, message)
                print(f"Nachricht gesendet: {message}")

