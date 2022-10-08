import RPi.GPIO as GPIO

class Parachute():
    def __init__(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(11, GPIO.OUT)
    
    def parachute_deployment():
        """Deploys the parachute.
        """
        GPIO.output(11,GPIO.HIGH)
        
    def kill_parachute_signal():
        """Kills the parachute signal to save electricity and prevent anything weird from happening.
        """
        GPIO.output(11,GPIO.LOW)
