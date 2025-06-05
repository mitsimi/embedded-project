from RpiMotorLib import RpiMotorLib
import threading
import time
import RPi.GPIO as GPIO

DIR_PIN = 22
STEP_PIN = 27
EN_PIN = 17

class StepperController:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DIR_PIN, GPIO.OUT)
        GPIO.setup(STEP_PIN, GPIO.OUT)
        GPIO.setup(EN_PIN, GPIO.OUT)
        GPIO.output(EN_PIN, GPIO.HIGH)
        GPIO_pins  = (-1, -1, -1)
        
        self.movement_queue = []
        self.is_running = False
        self.MAX_ROT = 650
        self.current_rot = 0
        
        self.direction = 22  # Direction -> GPIO Pin
        self.step = 27  # Step -> GPIO Pin
        print("init stepper")
        self.stepper_motor = RpiMotorLib.A4988Nema(self.direction, self.step, GPIO_pins , "A4988")
        
        t = threading.Thread(target=self.__move_stepper_thread)
        t.start()
        

    def __test__(self):
        print("Starting Stepper motor test.")
        self.stepper_motor.motor_go(False, "Full", 100, .01, False, .05)
        print("Stepper motor test completed.")
        
    def __move_stepper_thread(self):
        GPIO.output(EN_PIN, GPIO.LOW)
        while len(self.movement_queue) > 0:
            self.is_running = True
            move, pulse = self.movement_queue.pop()
            
            if move == 0:
                self.move_stepper_to_position(pulse)
            elif move == 1:
                self.move_stepper_direction(pulse)
            else: 
                print("invalid move: "+ str(move))

            print(f"current rot: {self.current_rot}")
        GPIO.output(EN_PIN, GPIO.HIGH)
        self.is_running = False
    
    def move_stepper_to_position(self, pulse):
        if pulse < 0 or pulse > self.MAX_ROT:
            print(f"invalid pulse (0 < pulse < {self.MAX_ROT})")
        else:
            print(f"move stepper to: {pulse}")
            self.stepper_motor.motor_go(pulse > self.current_rot, "Full", abs(pulse - self.current_rot), .01, False, .05)
            self.current_rot = pulse
                
        
     
    def move_stepper_direction(self, pulse):
        if (self.current_rot + pulse) < 0 or (self.current_rot + pulse) > self.MAX_ROT:
            print(f"invalid pulse (0 < pulse + current_rot: {self.current_rot} < {self.MAX_ROT})")
        else:
            print(f"move stepper: {pulse}")
            self.stepper_motor.motor_go(pulse > 0, "Full", abs(pulse), .01, False, .05)
            self.current_rot += pulse
            
            
    def add_queue_command(self,move,pulse):
        self.movement_queue.append((move, pulse))
        print(self.movement_queue)
        
        if not self.is_running:
            self.__move_stepper_thread()

    def exit(self):
        print("stop stepper")
        self.stepper_motor.motor_stop()
        GPIO.output(EN_PIN, GPIO.HIGH)


# def main():
#     pass
#     stepper = StepperController()
#     stepper.add_queue_command(1,100)
#     stepper.add_queue_command(1,-50)
#     stepper.add_queue_command(0,300)
#     stepper.add_queue_command(0,10)
#     stepper.__test__()
#     GPIO.cleanup()



# if __name__ == "__main__":
#     main()
    