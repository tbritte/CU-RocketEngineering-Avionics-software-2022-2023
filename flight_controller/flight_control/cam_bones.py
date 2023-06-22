# Sets the angle of the camera servo to the given angle
import RPi.GPIO as GPIO
import time

class CamBones:
    def __init__(self, pin):
        """
        :param gopro_num: The number of the GoPro (1, 2, or 3)
        """
        self.pin = pin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)

        self.activated_time = 0
        self.deactivated_time = 0

    def activate_camera(self):
        print("\n\nACTIVATING Bones {}\n\n".format(self.pin))
        GPIO.output(self.pin, GPIO.HIGH)

    def update(self):
        # If the button has been let go for 2 seconds, put the servo in a dead state
        if time.time() - self.deactivated_time > 2:
            GPIO.output(self.pin, GPIO.LOW)