import paho.mqtt.client as mqtt
from inputs import get_gamepad
import time

broker = "mqtt.eclipseprojects.io"
topic = "controller/input"

client = mqtt.Client()
client.connect(broker, 1883, 60)

last_values = {0: 0, 1: 0, 2: 0, 3: 0, 6: 0} 

scale_factor = 0.1 

threshold = 5 

def calculate_delta(current, last):
    delta = int((current - last) * scale_factor)
    
    # fine tuning versuch:
    speed_factor = max(1, abs(delta) / 20)  
    adjusted_delta = int(delta * speed_factor)
    
    return adjusted_delta if abs(adjusted_delta) > threshold else 0

print("Drücke einen Knopf..")

while True:
    events = get_gamepad()
    no_input = True 

    for event in events:
        if event.ev_type == "Absolute":  
            channel = None
            
            if event.code == "ABS_X":
                channel = 0
            elif event.code == "ABS_Y":
                channel = 1
            elif event.code == "ABS_RX":
                channel = 2
            elif event.code == "ABS_RY":
                channel = 3
            elif event.code == "ABS_Z": 
                channel = 6
            
            if channel is not None:
                delta = calculate_delta(event.state, last_values[channel])
                
                if delta != 0:  # weiß nicht obs nen großen Unterschied macht, aber um "unnötige" inputs zu ignorieren
                    last_values[channel] = event.state  
                    message = f"{channel}:1:{delta}" 
                    client.publish(topic, message)
                    print(f"Nachricht gesendet: {message}")
                    no_input = False

        elif event.ev_type == "Key" and event.state == 1:
            if event.code == "BTN_SOUTH":
                message = "2"
                client.publish(topic, message)
                print(f"Nachricht gesendet: {message}")
                no_input = False

    if no_input:
        time.sleep(0.1)

