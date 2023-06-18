"""
This is a simplified version of SRAD2
It will use its sensors to detect apogee to then deploy payload
It will use buddyComm to know when to turn on GoPros 2 and 3
It will not use buddyComm for anything else such as apogee because buddyComm is extremely unreliable
"""

import time
import RPi.GPIO as GPIO
from .modular_ext_sensor_handler import ModDataHandler
from .sim_telemetry_handler import SimTelemetryHandler
from .flight_status import FlightStatus, Stage
from .cam_servo import CamServoController
from .buddy_comm import BuddyCommSystem
from .buzzer import Buzzer

cam2 = 17  # Servo connects to GPIO 17 (6 down from top left), ground (5 down from top left) and 5v source (top right)
cam3 = 11

use_sim = False

def main():
    buddy_comm = BuddyCommSystem()
    buzzer = Buzzer()
    flight_status = FlightStatus(buzzer)

    gopro_2 = CamServoController(cam2)
    gopro_3 = CamServoController(cam3)

    if not use_sim:
        data_handler = ModDataHandler()
    else:
        data_handler = SimTelemetryHandler()

    terminate = False
    deployed_payload = False

    last_flight_status_update = time.time()

    while not terminate:
        """Data and flight status update"""
        data = data_handler.get_data()
        if time.time() - last_flight_status_update > .125:  # Update flight status every 1/8th of a second
            last_flight_status_update = time.time()
            flight_status.new_telemetry(data)

        print(flight_status.stage, flight_status.altitude_list[-1])

        """Checking if I should deploy the payload"""
        if not deployed_payload and flight_status.stage == Stage.DESCENT:
            deployed_payload = True
            buddy_comm.send(0)  # 00 - Payload deployed
            print("----Deploying payload----")
            # STUFF NEEDS TO GO HERE AT SOME POINT

        """Checking which GoPros I should turn on"""
        if buddy_comm.check_num(2):
            gopro_2.activate_camera()
        if buddy_comm.check_num(3):
            gopro_3.activate_camera()

        # Updating the GoPros' servo positions
        gopro_2.update()
        gopro_3.update()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        print("Cleaning up GPIO")
        GPIO.cleanup()
        print("Done")

