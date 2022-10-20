import RPi.GPIO as GPIO

class Parachute():
    def __init__(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
    
    def deploy(self):
        """Deploys the parachute.
        """
        GPIO.output(18,GPIO.HIGH)
        
    def kill_signal(self):
        """Kills the parachute signal to save electricity and prevent anything weird from happening.
        """
        GPIO.output(18,GPIO.LOW)
