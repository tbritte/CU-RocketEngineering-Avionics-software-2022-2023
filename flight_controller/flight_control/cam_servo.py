# Sets the angle of the camera servo to the given angle
import RPi.GPIO as GPIO
import time

CAM_SERVO_PIN = 17

class CamServoController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CAM_SERVO_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(CAM_SERVO_PIN, 50)
        self.pwm.start(2.5)
        self.active = False
        self.activated_time = 0

    def activate_camera(self):
        self.pwm.ChangeDutyCycle(13)
        self.active = True
        self.activated_time = time.time()

    def check_let_go_of_button(self):
        if self.active and time.time() - self.activated_time > 0.5:
            self.pwm.ChangeDutyCycle(2.5)
            self.active = False

    def terminate(self):
        self.pwm.stop()