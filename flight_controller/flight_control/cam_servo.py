# Sets the angle of the camera servo to the given angle
import RPi.GPIO as GPIO
import time

CAM_SERVO_PINS = [26, 8, 23]   # cam servos 1, 2, and 3's pins

class CamServoController:
    def __init__(self, gopro_num):
        """
        :param gopro_num: The number of the GoPro (1, 2, or 3)
        """
        self.num = gopro_num
        pin = CAM_SERVO_PINS[gopro_num - 1]

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(2.5)  # Puts the servo where it's far from pushing the button
        self.button_depressed = False
        self.activated_time = 0
        self.deactivated_time = 0

    def activate_camera(self):
        print("\n\nACTIVATING CAMERA {}\n\n".format(self.num))
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