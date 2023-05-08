# Sets the angle of the camera servo to the given angle
import RPi.GPIO as GPIO
import time

CAM_SERVO_PIN = 22

class CamServoController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CAM_SERVO_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(CAM_SERVO_PIN, 50)
        self.pwm.start(2.5)  # Puts the servo where it's far from pushing the button
        self.button_depressed = False
        self.activated_time = 0
        self.deactivated_time = 0

    def activate_camera(self):
        print("\n\nACTIVATING CAMERA\n\n")
        self.pwm.start(13)
        self.pwm.ChangeDutyCycle(13)
        self.button_depressed = True
        self.activated_time = time.time()

    def update(self):
        # print("(gopro) UPDATING CAMERA")
        self.check_let_go_of_button()  # Checks if the button has been held for 1 second and let's go
        # If the button has been let go for 2 seconds, put the servo in a dead state
        if not self.button_depressed and time.time() - self.deactivated_time > 2:
            self.pwm.ChangeDutyCycle(0)  # Puts the servo in a dead state to save power

    def check_let_go_of_button(self):
        if self.button_depressed and time.time() - self.activated_time > 1:  # If the button has been held for 1 second
            self.pwm.ChangeDutyCycle(2.5)  # Stops pushing the button
            self.deactivated_time = time.time()  # Records the time the button was let go
            self.button_depressed = False  # Sets the button to not be depressed

    def terminate(self):
        self.pwm.stop()