from subprocess import call
import time
import datetime
import random

from .parachute import Parachute

from .flight_status import FlightStatus
from .flight_status import Stage

from .telemetry_downlink import TelemetryDownlink
from .telemetry_handler import TelemetryHandler

from .data_logging import DataLogger

from .camera import Camera
from .LED_controller import LEDController
from .buzzer import Buzzer

start_time = time.time()
date = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
telemetry_logger = DataLogger(date + '-telemetry_log' + "-r" + str(random.randint(1000, 9999)) + '.csv', ['time','state', 'altitude', 'data_pulls', 'humidity', 'pressure', 'humidity_temp',
                                                    'pressure_temp', 'temp', 'roll', 'pitch', 'yaw', 'aclx', 'acly', 'aclz',
                                                    'north', 'magx', 'magy', 'magz'], start_time)

MAIN_CHUTE_DEPLOY_ALT = 1500


def startup(telemetryHandler: TelemetryHandler, telemetryDownlink: TelemetryDownlink):
    telemetryHandler.setup()
    telemetryDownlink.run()


def main():
    telemetry_handler = TelemetryHandler()
    # telemetry_downlink = TelemetryDownlink("Telemetry Downlink", 1000)

    # startup(telemetryHandler=telemetry_handler, telemetryDownlink=telemetry_downlink)
    telemetry_handler.setup()

    buzzer = Buzzer()

    flight_status = FlightStatus(telemetry_handler.sense, buzzer)
    parachute = Parachute()

    camera = Camera()
    led_controller = LEDController(telemetry_handler.sense, flight_status, camera)

    buzzer.start_up_buzz()  # Three short beeps to indicate that main is being run

    buzzer.main_chute_deploy_alt_buzz(MAIN_CHUTE_DEPLOY_ALT)  # Indicates the altitude for main chute deployment

    terminate = False

    last_data_pull = time.time()

    cycle = 0
    data_pulls = 0

    while not terminate:
        cycle += 1
        if time.time() - last_data_pull > 0.125:  # Changed to 8hz because get_data can't run at 16hz
            last_data_pull = time.time()
            data_pulls += 1
            print(flight_status.stage.name)
            data = telemetry_handler.get_data()
            data['state'] = flight_status.current_stage_name()
            data['data_pulls'] = data_pulls
            telemetry_logger.log_data(data)
            # telemetryDownlink.send_data(data)
            flight_status.new_telemetry(data)
            led_controller.update_lights()

        buzzer.update()

        if flight_status.current_stage() == Stage.PRE_FLIGHT:
            if not camera.recording:
                camera.start_recording()
        if flight_status.current_stage() == Stage.DESCENT and not parachute.deployed:
            parachute.deploy()
        elif flight_status.current_stage() == Stage.DESCENT and parachute.deployed:
            parachute.kill_signal()
        elif flight_status.current_stage() == Stage.ON_GROUND:
            if camera.recording:
                camera.stop_recording()
            terminate = True

    call(['shutdown', '-h', 'now'], shell=False)


if __name__ == '__main__':
    main()
