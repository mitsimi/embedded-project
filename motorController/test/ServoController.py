import threading
import time

import Adafruit_PCA9685
import Adafruit_GPIO.I2C as I2C

class ServoController:

    def __init__(self):
        """
        Initializes the ServoController class, setting up the PWM controller, servos,
        and their initial positions. Starts a thread to handle servo movements.
        """
        self.__setup_pwm()
        self.__setup_servos()
        self.__setup_initial_servo_position()

        self.movement_queue = []
        self.__queue_lock = threading.Lock()

        self.setup_sleep_time = 0.0

        self.step_size = 1
        self.sleep_time = 0.006

        self.__move_servo_thread_running = True
        self.__move_servo_thread = threading.Thread(target=self.__move_servo_thread, daemon=True)
        self.__move_servo_thread.start()





    def __setup_pwm(self):
        """
        Sets up the PWM controller with the specified address and frequency.
        """
        I2C.get_default_bus = lambda: 1
        self.__pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.__pwm.set_pwm_freq(50)

    def __setup_servos(self):
        """
        Configures the servos with their respective channels, minimum and maximum pulse values,
        and default positions.
        """
        gripper = (0, 100, 380, 100)  # channel, min_pulse, max_pulse, default_pulse
        gripper_arm = (1, 100, 500, 320)
        upper_arm = (2, 100, 470, 100)
        middle_arm = (3, 100, 520, 100)
        lower_arm_a = (4, 220, 480, 350)
        lower_arm_b = (5, 170, 430, 300)

        self.__servos = [gripper, gripper_arm, upper_arm, middle_arm, lower_arm_a, lower_arm_b]

    def __setup_initial_servo_position(self):
        """
        Initializes the current and current after move positions of the servos to their default values.
        """
        self.current_servo_position = []
        self.current_servo_position_after_move = []
        for servo in self.__servos:
            self.current_servo_position.append(servo[3])
            self.current_servo_position_after_move.append(servo[3])

    def move_servo_to_position(self, channel, target_pulse):
        """
        Adds a movement command to the queue to move a servo to a specific position.

        :param channel: The channel of the servo to move.
        :param target_pulse: The target position for the servo.
        """
        if (channel >= 0) and (channel < len(self.__servos)-1):
            _, min_pulse, max_pulse, _ = self.__servos[channel]
            if min_pulse <= target_pulse <= max_pulse:
                with self.__queue_lock:
                    self.movement_queue.append((channel, target_pulse))
            else:
                print("Pulse out of range!")
        else:
            print("Channel not available!")

    def move_servo_direction(self, channel, direction):
        """
        Adds a movement command to the queue to move a servo in a specific direction.

        :param channel: The channel of the servo to move.
        :param direction: The direction to move the servo (positive or negative).
         """
        _ , min_pulse, max_pulse, _ = self.__servos[channel]

        if (channel >= 0) and (channel < len(self.__servos)-1):
            with self.__queue_lock:
                servo_position = self.__future_servo_position()
                if min_pulse >= servo_position[channel] + direction:
                    self.movement_queue.append((channel, min_pulse))
                if max_pulse <= servo_position[channel] + direction:
                    self.movement_queue.append((channel, max_pulse))
                else:
                    self.movement_queue.append((channel, servo_position[channel] + direction))
        else:
            print("Channel not available!")

    def __future_servo_position(self):
        """
        Calculates the future position of the servos after all queued movements are completed.

        :return: A list of the future positions of the servos.
        """
        future_servo_position = self.current_servo_position_after_move.copy()
        for channel, pulse in self.movement_queue:
            if channel == 4 or channel == 5:
                future_servo_position[4] = pulse
                future_servo_position[5] = 650 - pulse
            else:
                future_servo_position[channel] = pulse

        return future_servo_position

    def move_default_servo_position(self):
        """
        Moves all servos to their default positions in reverse order to start with the base.
        """
        for servo in reversed(self.__servos):
            channel = servo[0]
            default_pulse = servo[3]
            if 0 <= channel <= 4:
                self.move_servo_to_position(channel, default_pulse)
                time.sleep(self.setup_sleep_time)

    def __move_servo_thread(self):
        """
        Continuously processes the movement queue and moves the servos to their target positions.
        """
        while self.__move_servo_thread_running:

            if len(self.movement_queue) != 0:
                with self.__queue_lock:
                    channel, target_pulse = self.movement_queue.pop(0)
                    if channel == 4 or channel == 5:
                        self.current_servo_position_after_move[4] = target_pulse
                        self.current_servo_position_after_move[5] = 650 - target_pulse
                    else:
                        self.current_servo_position_after_move[channel] = target_pulse

                if (channel >= 0) and (channel < len(self.__servos)-1):
                    print(f"Start to Move Servo: {channel} to {target_pulse}")

                    _ , min_pulse, max_pulse, _ = self.__servos[channel]

                    if min_pulse <= target_pulse <= max_pulse:

                        if target_pulse < self.current_servo_position[channel]:
                            current_step_size = -1 * self.step_size
                        else:
                            current_step_size = self.step_size

                        for pulse in range(self.current_servo_position[channel], target_pulse + current_step_size, current_step_size):
                            if pulse > (target_pulse - current_step_size) and current_step_size > 0 or pulse < (target_pulse - current_step_size) and current_step_size < 0:
                                pulse = target_pulse

                            if channel == 4 or channel == 5:
                                b_pulse = 650 - pulse

                                self.__pwm.set_pwm(4, 0, pulse)
                                self.__pwm.set_pwm(5, 0, b_pulse)

                                self.current_servo_position[4] = pulse
                                self.current_servo_position[5] = b_pulse

                            else:
                                self.__pwm.set_pwm(channel, 0, pulse)
                                self.current_servo_position[channel] = pulse

                            time.sleep(self.sleep_time)
                    else:
                        print("Pulse out of range!")
                else:
                    print("Channel not available!")

    def exit(self):
        """
        Stops the servo movement thread, disables the servos, and exits the program.
        """
        self.__move_servo_thread_running = False
        self.__move_servo_thread.join()

        self.__disable_servos()
        print("Exit ServoController")

    def __disable_servos(self):
        """
        Disables all servos by setting their pulse width to 0.
        """
        for servo in self.__servos:
            channel = servo[0]

            self.__pwm.set_pwm(channel, 0, 0)
            self.current_servo_position[channel] = 0
            self.current_servo_position_after_move[channel] = 0

