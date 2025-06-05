import sys
import paho.mqtt.client as mqtt
from ServoController import ServoController

def main():
    servo_controller = ServoController()
    servo_controller.move_default_servo_position()

    print("Enter a Motor Movement: 'channel:move:pulse':")
    for line in sys.stdin:
        input_str = line.strip().lower()
        if input_str == "exit":
            print("Exit Programm.")
            servo_controller.exit()
            sys.exit()
        try:
            parsed = input_str.split(":")
            channel = int(parsed[0])
            move = int(parsed[1])
            target_pulse = int(parsed[2])

            if move == 0:
                servo_controller.move_servo_to_position(channel, int(target_pulse))
            if move == 1:
                servo_controller.move_servo_direction(channel, int(target_pulse))
            if move == 2:
                servo_controller.move_default_servo_position()
        except Exception as e:
            print(f"Fehler: {e}")

if __name__ == "__main__":
    main()