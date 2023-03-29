import RPi.GPIO as GPIO

class Parachute:
    def __init__(self, pin) -> None:
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.deployed = False
    
    def deploy(self):
        """Deploys the parachute.
        """
        GPIO.output(self.pin, GPIO.HIGH)
        self.deployed = True
        
    def kill_signal(self):
        """Kills the parachute signal to save electricity and prevent anything weird from happening.
        """
        GPIO.output(self.pin, GPIO.LOW)
