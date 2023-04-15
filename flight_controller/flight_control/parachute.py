import RPi.GPIO as GPIO
import time


class Parachute:
    def __init__(self, pin) -> None:
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self.deployed = False
        self.deploy_time = 0

    def deploy(self):
        """Deploys the parachute.
        """
        print("DEPLOY CALLED PIN IS", self.pin)
        GPIO.output(self.pin, GPIO.HIGH)
        self.deployed = True
        self.deploy_time = time.time()

    def update(self):
        """
        Kills the parachute signal after .5 seconds of being set to high
        """
        if self.deployed and time.time() - self.deploy_time > .5:
            self._kill_signal()

    def _kill_signal(self):
        """Kills the parachute signal to save electricity and prevent anything weird from happening.
        """
        GPIO.output(self.pin, GPIO.LOW)
