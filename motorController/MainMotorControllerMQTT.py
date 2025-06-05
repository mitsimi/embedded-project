import paho.mqtt.client as mqtt

from ServoController import ServoController
from StepperController import StepperController

SUBSCRIBE_TOPIC_WEB = "web/input"
SUBSCRIBE_TOPIC_CONTROLLER = "controller/input"
STEPPER_CHANNEL = 6

servo_controller = ServoController()
stepper_controller = StepperController()
servo_controller.move_default_servo_position()

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}`")
    

    #print("channel:move:pulse")
    
    
    
    input_str = msg.payload.decode().strip().lower()
    if input_str == "exit":
        print("Exit Programm.")
        servo_controller.exit()
        stepper_controller.exit()
        sys.exit()
    try:
        parsed = input_str.split(":")
        channel = int(parsed[0])
        move = int(parsed[1])
        target_pulse = int(parsed[2])

        if channel == STEPPER_CHANNEL:
            stepper_controller.add_queue_command(move,target_pulse)
        else:
            if move == 0:
                servo_controller.move_servo_to_position(channel, int(target_pulse))
            if move == 1:
                servo_controller.move_servo_direction(channel, int(target_pulse))
            if move == 2:
                servo_controller.move_default_servo_position()
    except Exception as e:
        print(f"Fehler: {e}")

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.subscribe(SUBSCRIBE_TOPIC_WEB)
client.subscribe(SUBSCRIBE_TOPIC_CONTROLLER)
client.on_message = on_message

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    servo_controller.exit()
    stepper_controller.exit()