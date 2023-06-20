import RPi.GPIO as GPIO
from .flight_status import Stage
import time

# mach lock at 1500 ft.
# must have been above 2000 ft to consider payload
# after main is payload
# Remove buddy comm stuff

class Parachute:
    """
    All of the pinouts have been disabled because those pins are now being reused for other functions
    """
    def __init__(self, pin) -> None:
        # self.pin = pin
        # GPIO.setwarnings(False)
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.pin, GPIO.OUT)
        # GPIO.output(self.pin, GPIO.LOW)
        self.deployed = False
        self.deploy_time = 0

    def deploy(self):
        """Deploys the parachute.
        """
        print("(Parachute)  DEPLOY")
        # GPIO.output(self.pin, GPIO.HIGH)
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
        # GPIO.output(self.pin, GPIO.LOW)
        pass


class ParachuteHandler:
    """
    Handles the deployment of all the rocket's parachutes
    """
    def __init__(self, flight_status, main_chute_deploy_alt, primary_drogue_pin, backup_drogue_pin, main_pin):
        """
        flight_status: Flight_Status object of the rocket which contains all the info needed to deploy the parachutes
        correctly
        """

        self.flight_status = flight_status  # Is passed by reference, so it is updated as the flight_status object is
        self.main_chute_deploy_alt = main_chute_deploy_alt

        # Create the parachute objects
        self.drogue_primary = Parachute(primary_drogue_pin)
        self.drogue_backup = Parachute(backup_drogue_pin)

        self.main = Parachute(main_pin)
        self.did_emergency_main = False

    def update(self, disarmed):
        if self.flight_status.current_stage() == Stage.DESCENT and not disarmed:
            if not self.drogue_primary.deployed:
                # If we are in descent and the first drogue charge hasn't been set off, set it off
                print("(Parachute Handler)  FIRST DROGUE CHARGE")
                self.drogue_primary.deploy()


            if self.flight_status.get_median_altitude_from_last_second() < self.main_chute_deploy_alt:
                if not self.main.deployed:
                    # If we are below the main chute deployment altitude, and the main chute hasn't been deployed,
                    # deploy it
                    print("(Parachute Handler)  MAIN DEPLOY")
                    self.main.deploy()

            """
            Processing if emergency parachute deployments are needed
            """

            if self.flight_status.drogue_failure:
                # We are falling at a critical speed, first we try to deploy the backup drogue
                if not self.drogue_backup.deployed:
                    print("(Parachute Handler) BACKUP DROGUE DEPLOY")
                    self.drogue_backup.deploy()

                if self.drogue_backup.deployed and not self.main.deployed and time.time() - self.drogue_backup.deploy_time > 2:
                    # We are still falling at a critical speed 2 seconds after trying the backup drogue,
                    # we deploy the main chute early
                    print("(Parachute Handler) EMERGENCY MAIN DEPLOY")
                    # self.main.deploy()
                    self.did_emergency_main = True
