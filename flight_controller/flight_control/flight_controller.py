from subprocess import call
import time
import datetime
import random

from .parachute import Parachute

from .flight_status import FlightStatus
from .flight_status import Stage

from .telemetry_downlink import TelemetryDownlink

from .telemetry_handler import TelemetryHandler
from .ext_telemetry_handler import ExtTelemetryHandler

from .data_logging import DataLogger

from .camera import Camera
from .LED_controller import LEDController
from .buzzer import Buzzer

from gpiozero import CPUTemperature

start_time = time.time()
date = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

MAIN_CHUTE_DEPLOY_ALT = 1500
USING_SENSE_HAT = False


def startup(telemetry_handler: TelemetryHandler, telemetry_downlink: TelemetryDownlink):
    telemetry_handler.setup()
    telemetry_downlink.run()


def main():

    drogue_deployed = False
    main_deployed = False

    if USING_SENSE_HAT:
        telemetry_handler = TelemetryHandler()  # Collects data from the sense hat
    else:
        telemetry_handler = ExtTelemetryHandler()  # Collects data from the external sensors

    # Creates a new data logger for the telemetry data depending on what sensors are being used
    telemetry_logger = DataLogger(date + '-telemetry_log' + "-r" + str(random.randint(1000, 9999)) + '.csv',
                                  telemetry_handler.get_data_header_list(), start_time)

    telemetry_handler.setup()

    telemetry_downlink = TelemetryDownlink()

    buzzer = Buzzer()

    flight_status = FlightStatus(buzzer)
    parachute = Parachute()

    cpu = CPUTemperature()  # For getting the CPU temperature

    camera = Camera()

    # Only set up the LED controller if the sense hat is being used
    if USING_SENSE_HAT:
        led_controller = LEDController(telemetry_handler.sense, flight_status, camera)
    else:
        led_controller = None

    buzzer.start_up_buzz()  # Three short beeps to indicate that main is being run

    buzzer.main_chute_deploy_alt_buzz(MAIN_CHUTE_DEPLOY_ALT)  # Indicates the altitude for main chute deployment

    terminate = False

    last_data_pull = time.time()
    last_downlink_send = time.time()
    last_flight_status_update = time.time()

    cycle = 0
    data_pulls = 0

    while not terminate:
        cycle += 1
        if True:  # run as fast as possible
            # print(time.time() - last_data_pull)  # To see how fast the loop is running
            last_data_pull = time.time()  # Allways pulling data

            data_pulls += 1

            data = telemetry_handler.get_data()
            data['state'] = flight_status.current_stage_name()
            data['data_pulls'] = data_pulls
            data['cputemp'] = cpu.temperature
            data['predicted_apogee'] = 0

            print("\n\n", data)
            
            status_bits = flight_status.collect_status_bits(data, drogue_deployed, main_deployed, camera.recording)

            try:
                if telemetry_downlink.ser is not None:
                    if (time.time() - last_downlink_send) > 0.125:  # Downlink should only be sent at 8hz 
                        telemetry_downlink.send_data(data, status_bits)
                        last_downlink_send = time.time()
            except:
                print("Error sending data to ground station")

            try:
                # Log the data to a csv file happens at 16hz
                telemetry_logger.log_data(data)
            except:
                print("Error logging data")

            try:
                if (time.time() - last_flight_status_update) > 0.125:  # Flight_status should only be updated at 8hz
                    flight_status.new_telemetry(data)
                    last_flight_status_update = time.time()
            except:
                print("Error updating flight status")

            if led_controller is not None:
                led_controller.update_lights()

        buzzer.update()

        if flight_status.current_stage() == Stage.PRE_FLIGHT:
            if not camera.recording:
                camera.start_recording()
        if flight_status.current_stage() == Stage.DESCENT and not parachute.deployed:
            parachute.deploy()
            drogue_deployed = True
        elif flight_status.current_stage() == Stage.DESCENT and parachute.deployed:
            parachute.kill_signal()
        # elif flight_status.current_stage() == Stage.ON_GROUND:
    #         if camera.recording:
    #             camera.stop_recording()
    #         terminate = True
    #
    # call(['shutdown', '-h', 'now'], shell=False)


if __name__ == '__main__':
    main()
