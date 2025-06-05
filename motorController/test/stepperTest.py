import RPi.GPIO as GPIO
import time
from RpiMotorLib import RpiMotorLib

# Pin definitions
DIR_PIN = 22
STEP_PIN = 27
EN_PIN = 17

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.output(EN_PIN, GPIO.LOW)
stepper_motor = RpiMotorLib.A4988Nema(DIR_PIN, STEP_PIN, (-1,-1,-1) , "A4988")

stepper_motor.motor_go(False, "Full", 100, .01, False, .05)

def rotate_stepper(direction, steps, delay=0.001):
    """
    Rotate the stepper motor.
    
    Parameters:
    - direction: 0 for clockwise, 1 for counter-clockwise
    - steps: number of steps to rotate
    - delay: time between steps in seconds (controls speed)
    """
    # Set direction
    GPIO.output(DIR_PIN, direction)
    
    # Step the motor
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

try:
    # Example usage
    print("Rotating clockwise 200 steps")
    #rotate_stepper(0, 200)  # Clockwise
    
    #time.sleep(1)  # Pause for 1 second
    
    print("Rotating counter-clockwise 200 steps")
    #rotate_stepper(1, 200)  # Counter-clockwise
    
except KeyboardInterrupt:
    print("\nProgram stopped by user")

finally:
    # Clean up GPIO
    GPIO.cleanup()
    print("GPIO cleaned up")