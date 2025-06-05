import pygame
import time
import paho.mqtt.client as mqtt

# MQTT configuration
broker = "localhost"
topic = "controller/input"
client = mqtt.Client()
client.connect(broker, 1883, 60)

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Check and initialize controller
if pygame.joystick.get_count() == 0:
    raise Exception("No controller found!")
controller = pygame.joystick.Joystick(0)
controller.init()
print(f"Controller connected: {controller.get_name()}")

# Configuration
thresholds = {0: 0.65, 1: 0.65, 2: 0.65, 3: 0.65, 4: 0.65, 5: 0.65}  # For analog inputs
active_channels = {0: False, 1: False, 2: False, 3: False, 4: False, 6: False}
last_sent_time = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 6: 0}
send_interval = 0.1  # seconds

# Step size configuration (can be adjusted)
step_size_positive = 15  # Default step size for positive direction
step_size_negative = -15  # Default step size for negative direction

# Calibration for analog inputs
print("Controller calibration - Please keep all sticks and triggers in neutral position...")
pygame.event.pump()
time.sleep(1)
offsets = {}

# Calibration of all analog axes
# Standard sticks (channels 0-1, 3)
for channel in [0, 1, 3]:
    try:
        offsets[channel] = round(controller.get_axis(channel), 2)
        print(f"Channel {channel} offset: {offsets[channel]}")
    except:
        offsets[channel] = 0.0
        print(f"Channel {channel} not available, offset set to 0.0")

# Calibration of triggers
try:
    # Left trigger (L2/LT) - can be axis 2 or 4
    offsets[2] = round(controller.get_axis(2), 2)
    print(f"Channel 2 (LT) offset: {offsets[2]}")
except:
    offsets[2] = 0.0
    print(f"Channel 2 (LT) not available on axis 2, offset set to 0.0")

try:
    offsets[4] = round(controller.get_axis(4), 2)
    print(f"Channel 4 (L2) offset: {offsets[4]}")
except:
    offsets[4] = 0.0
    print(f"Channel 4 (L2) not available, offset set to 0.0")

try:
    # Right trigger (R2/RT)
    offsets[5] = round(controller.get_axis(5), 2)
    print(f"Channel 5 (RT) offset: {offsets[5]}")
except:
    offsets[5] = 0.0
    print(f"Channel 5 (RT) not available, offset set to 0.0")

print("Calibration completed.")


def get_stick_position(value, channel):
    adjusted_value = round(value - offsets.get(channel, 0), 2)
    threshold = thresholds.get(channel, 0.65)

    if -threshold <= adjusted_value <= threshold:
        return 0
    elif adjusted_value < -threshold:
        return step_size_negative
    elif adjusted_value > threshold:
        return step_size_positive


try:
    while True:
        pygame.event.pump()
        current_time = time.time()

        # Read standard sticks (channels 0, 1, 3)
        for channel in [0, 1, 3]:
            raw_value = round(controller.get_axis(channel), 2)
            direction = get_stick_position(raw_value, channel)

            if direction != 0:
                if not active_channels[channel] or (current_time - last_sent_time[channel]) >= send_interval:
                    message = f"{channel}:1:{direction}"
                    client.publish(topic, message)
                    print(f"Sent: {message}")
                    last_sent_time[channel] = current_time
                    active_channels[channel] = True
            elif active_channels[channel]:
                active_channels[channel] = False
                print(f"Channel {channel}: Stick in neutral position")

        # Channel 2: LT (negative) and RT (positive)
        try:
            # LT is typically axis 2 or 4
            lt_value = controller.get_axis(2)
            # RT is typically axis 5
            rt_value = controller.get_axis(5)

            # Combined value: LT pressed gives negative, RT pressed gives positive
            trigger_value = 0
            if abs(lt_value - offsets.get(2, 0)) > 0.5:  # LT pressed with offset consideration
                trigger_value = step_size_negative
            elif abs(rt_value - offsets.get(5, 0)) > 0.5:  # RT pressed with offset consideration
                trigger_value = step_size_positive

            if trigger_value != 0:
                if not active_channels[2] or (current_time - last_sent_time[2]) >= send_interval:
                    message = f"2:1:{trigger_value}"
                    client.publish(topic, message)
                    print(f"Sent: {message}")
                    last_sent_time[2] = current_time
                    active_channels[2] = True
            elif active_channels[2]:
                active_channels[2] = False
                print(f"Channel 2: Triggers in neutral position")
        except:
            pass

        # Additional channel 4 - left trigger (L2)
        try:
            trigger_left = controller.get_axis(4)  # Typically L2
            direction_4 = get_stick_position(trigger_left, 4)

            if direction_4 != 0:
                if not active_channels[4] or (current_time - last_sent_time[4]) >= send_interval:
                    message = f"4:1:{direction_4}"
                    client.publish(topic, message)
                    print(f"Sent: {message}")
                    last_sent_time[4] = current_time
                    active_channels[4] = True
            elif active_channels[4]:
                active_channels[4] = False
                print(f"Channel 4: In neutral position")
        except:
            pass

        # Channel 5 is skipped as requested

        # Channel 6: LB (negative) and RB (positive) - shoulder buttons are digital (buttons)
        try:
            # LB is typically button 4
            lb_pressed = controller.get_button(4)
            # RB is typically button 5
            rb_pressed = controller.get_button(5)

            button_value = 0
            if lb_pressed:
                button_value = step_size_negative
            elif rb_pressed:
                button_value = step_size_positive

            if button_value != 0:
                if not active_channels[6] or (current_time - last_sent_time[6]) >= send_interval:
                    message = f"6:1:{button_value}"
                    client.publish(topic, message)
                    print(f"Sent: {message}")
                    last_sent_time[6] = current_time
                    active_channels[6] = True
                    time.sleep(0.5)  # Small delay to avoid rapid firing
            elif active_channels[6]:
                active_channels[6] = False
                print(f"Channel 6: Shoulder buttons in neutral position")
        except Exception as e:
            print(f"Error with shoulder buttons: {e}")

        # Button A for reset
        if controller.get_button(0):
            message = "0:2:0"
            client.publish(topic, message)
            print(f"Sent: {message}")
            time.sleep(0.3)

        # Button B (1) for recalibration
        if controller.get_button(1):
            print("Recalibration...")
            # Recalibrate all analog channels
            for ch in [0, 1, 3]:
                try:
                    offsets[ch] = round(controller.get_axis(ch), 2)
                    print(f"Channel {ch} new offset: {offsets[ch]}")
                except:
                    pass

            # Recalibrate triggers
            try:
                offsets[2] = round(controller.get_axis(2), 2)
                print(f"Channel 2 (LT) new offset: {offsets[2]}")
            except:
                pass

            try:
                offsets[4] = round(controller.get_axis(4), 2)
                print(f"Channel 4 (L2) new offset: {offsets[4]}")
            except:
                pass

            try:
                offsets[5] = round(controller.get_axis(5), 2)
                print(f"Channel 5 (RT) new offset: {offsets[5]}")
            except:
                pass

            time.sleep(0.3)

except KeyboardInterrupt:
    print("Program terminated")
except Exception as e:
    print(f"Error: {e}")
finally:
    pygame.quit()