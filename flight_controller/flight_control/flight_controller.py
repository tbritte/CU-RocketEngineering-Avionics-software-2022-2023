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
from .sim_telemetry_handler import SimTelemetryHandler

from .buddy_comm import BuddyComm

from .data_logging import DataLogger

from .camera import Camera
from .cam_servo import CamServoController

from .LED_controller import LEDController
from .buzzer import Buzzer

from gpiozero import CPUTemperature

start_time = time.time()
date = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

# Main chute deploy altitude in meters
MAIN_CHUTE_DEPLOY_ALT = 304.8
USING_SENSE_HAT = False
USING_SIM_DATA = True


def startup(telemetry_handler: TelemetryHandler, telemetry_downlink: TelemetryDownlink):
    telemetry_handler.setup()
    telemetry_downlink.run()


def main():

    drogue_deployed = False
    main_deployed = False

    if USING_SIM_DATA:
        telemetry_handler = SimTelemetryHandler() # Uses previously collected data in a csv file
    else:
        if USING_SENSE_HAT:
            telemetry_handler = TelemetryHandler()  # Collects data from the sense hat
        else:
            telemetry_handler = ExtTelemetryHandler()  # Collects data from the external sensors

    # Creates a new data logger for the telemetry data depending on what sensors are being used
    telemetry_logger = DataLogger(date + '-telemetry_log' + "-r" + str(random.randint(1000, 9999)) + '.csv',
                                  telemetry_handler.get_data_header_list(), start_time)

    telemetry_handler.setup()

    telemetry_downlink = TelemetryDownlink()
    buddy_comm = BuddyComm()

    buzzer = Buzzer()

    flight_status = FlightStatus(buzzer)
    drogue_chute = Parachute(18)
    main_chute = Parachute(16)

    cpu = CPUTemperature()  # For getting the CPU temperature

    camera = Camera()
    go_pro_1_cam_servo = CamServoController()


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

            print("\n\n STATUS: ", flight_status.current_stage_name())
            # print("\n\n", data)
            
            status_bits = flight_status.collect_status_bits(data, drogue_deployed, main_deployed, camera.recording)
            print(status_bits)
            try:
                if telemetry_downlink.ser is not None:
                    # DON'T CHANGE DOWNLINK SPEED UNLESS YOU CHANGE GPS SAME TIME INCREMENT AMOUNT FROM .125
                    if (time.time() - last_downlink_send) > 0.125:  # Downlink should only be sent at 8hz 
                        telemetry_downlink.send_data(data, status_bits)
                        last_downlink_send = time.time()
            except Exception as e:
                print("Error sending data to ground station " + str(e))

            try:
                if telemetry_downlink.ser is not None:
                    read_num = telemetry_downlink.read_data()
                    if read_num == 1:
                        # Start go pro 1
                        print("Trying to start GoPro 1")
                        go_pro_1_cam_servo.activate_camera()
                        if flight_status.go_pro_1_on:
                            flight_status.go_pro_1_on = False
                        else:
                            flight_status.go_pro_1_on = True

                    elif read_num == 2:
                        # TELL SRAD2 TO TURN GOPRO2 ON
                        pass
                    elif read_num == 3:
                        # TELL SRAD2 TO TURN GOPRO3 ON
                        pass
            except Exception as e:
                print("Error reading data from ground station " + str(e))

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

            # Handling what the SRAD2 tells us
            num_from_srad2 = buddy_comm.receive()
            if num_from_srad2 != -1:
                if num_from_srad2 == 0:
                    flight_status.payload_deployed = True
                    print("(buddy) Payload deployed")
                elif num_from_srad2 == 1:
                    flight_status.go_pro_2_on = True
                    print("(buddy) GoPro 2 on")
                elif num_from_srad2 == 2:
                    pass
                    print("(buddy) SRAD2 is armed and flight ready")
                elif num_from_srad2 == 3:
                    flight_status.go_pro_3_on = True
                    print("(buddy) GoPro 3 on")

            if led_controller is not None:
                led_controller.update_lights()

        buzzer.update()
        go_pro_1_cam_servo.check_let_go_of_button()

        if flight_status.current_stage() == Stage.PRE_FLIGHT:
            if not camera.recording:
                camera.start_recording()
        if flight_status.current_stage() == Stage.DESCENT and not drogue_chute.deployed:
            drogue_chute.deploy()
            drogue_deployed = True
        elif flight_status.current_stage() == Stage.DESCENT and drogue_chute.deployed:
            drogue_chute.kill_signal()
        if flight_status.current_stage() == Stage.DESCENT and flight_status.get_median_altitude_from_last_second() < MAIN_CHUTE_DEPLOY_ALT and not main_chute.deployed:
            print("MAIN DEPLOY")
            main_chute.deploy()
            main_deployed = True
        # elif flight_status.current_stage() == Stage.ON_GROUND:
    #         if camera.recording:
    #             camera.stop_recording()
    #         terminate = True
    #
    # call(['shutdown', '-h', 'now'], shell=False)


if __name__ == '__main__':
    main()
