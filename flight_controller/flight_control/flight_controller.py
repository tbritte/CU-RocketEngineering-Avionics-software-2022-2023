from subprocess import call
import time
import datetime
import random

from .parachute import Parachute

from .flight_status import FlightStatus
from .flight_status import Stage

from .telemetry_downlink import TelemetryDownlink

from .telemetry_handler import TelemetryHandler
from .ext_telemetry_handler import extTelemThread
from .sim_telemetry_handler import SimTelemetryHandler

from .buddy_comm import BuddyCommSystem

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
DROGUE_CHUTE_PIN = 25
MAIN_CHUTE_PIN = 17

USING_SENSE_HAT = False
USING_SIM_DATA = False


# def startup(telemetry_handler: TelemetryHandler, telemetry_downlink: TelemetryDownlink):
#     telemetry_handler.setup()
#     telemetry_downlink.run()


def data_pprint(data: dict):
    """
    Prints out the data in the nicer format i.e. two columns
    :param data: A dictionary of values
    """

    # Find the longest key
    longest_key = 0
    for key in data.keys():
        if len(key) > longest_key:
            longest_key = len(key)

    # Print out the data
    for key in data.keys():
        print(key + " " * (longest_key - len(key)) + ":", data[key])


def alt_bat_test():
    """
    Tests how long altitude came be collected before the battery drains. Also heat testing
    """
    input("PRESS ENTER TO START ALT_BAT_TEST")  # Wait for user to press enter to prevent auto start

    telemetry_handler = extTelemThread()

    header_list = ["time (s)", "altitude", "temp", "cputemp"]  # Not using the full header list from the telemetry handler

    telemetry_logger = DataLogger(date + '-alt_bat_test_log' + "-r" + str(random.randint(1000, 9999)) + '.csv',
                                  header_list, start_time)
    cpu = CPUTemperature()  # For getting the CPU temperature

    time_of_last_loop = time.monotonic()
    while True:
        if time.monotonic() - time_of_last_loop > 1:
            print("Main loop time:", time.monotonic() - time_of_last_loop)
            time_of_last_loop = time.monotonic()
            all_data = telemetry_handler.get_data()  # Includes data from other sensors that we do not need

            # Using just the altitude and temperature data that we need for the test
            data = {"time (s)": time.time() - start_time,
                    "altitude": all_data["altitude"],
                    "temp": all_data["bar_temp"],
                    "cputemp": cpu.temperature}

            telemetry_logger.log_data(data)

            data_pprint(data)


def main():
    hello = input("PRESS ENTER TO START")
    drogue_deployed = False
    main_deployed = False

    drogue_chute = Parachute(DROGUE_CHUTE_PIN)
    main_chute = Parachute(MAIN_CHUTE_PIN)

    if USING_SIM_DATA:
        telemetry_handler = SimTelemetryHandler()  # Uses previously collected data in a csv file
    else:
        if USING_SENSE_HAT:
            telemetry_handler = TelemetryHandler()  # Collects data from the sense hat
        else:
            telemetry_handler = extTelemThread()  # Collects data from the external sensors

    # Creates a new data logger for the telemetry data depending on what sensors are being used
    telemetry_logger = DataLogger(date + '-telemetry_log' + "-r" + str(random.randint(1000, 9999)) + '.csv',
                                  telemetry_handler.get_data_header_list(), start_time)

    telemetry_downlink = TelemetryDownlink()
    buddy_comm = BuddyCommSystem()  # Used for receiving data operates in a separate thread

    buzzer = Buzzer()

    flight_status = FlightStatus(buzzer)

    override_mode = False
    disarmed = False
    disarmed_time = time.time()

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

    SERVO_TEST_TIME = 0
    buddy_sends = 0
    time_of_last_buddy_send = time.time() + 15

    # For testing the cameras
    # go_pro_1_cam_servo.activate_camera()

    while not terminate:
        cycle += 1
        try:
            print("(Timing) Time sense last data pull:",
                  time.time() - last_data_pull)  # To see how fast the loop is running
            last_data_pull = time.time()  # Always pulling data

            data_pulls += 1

            # if time.time() - time_of_last_buddy_send > 5:
            #     time_of_last_buddy_send = time.time()
            #     buddy_sends += 1
            #     v = buddy_sends % 4
            #     buddy_comm.send(v)
            #     print("\n\nSent a ", v, " to SRAD2\n\n")

            # time_before_get_data = time.time()
            data = telemetry_handler.get_data()
            # print("Time taken to do telemetry handler.get_data(): ", time.time() - time_before_get_data)

            data['state'] = flight_status.current_stage_name()
            data['data_pulls'] = data_pulls
            data['cputemp'] = cpu.temperature
            data['predicted_apogee'] = 0

            print("STATUS: ", flight_status.current_stage_name())
            # print("Buddy Comm messages: ", buddy_comm.get_messages())
            print("Data: ", data)

            # print("\n\n", data)

            status_bits = flight_status.collect_status_bits(data, drogue_deployed, main_deployed, camera.recording,
                                                            disarmed)
            # print(status_bits)
            try:
                if telemetry_downlink.ser is not None:
                    # DON'T CHANGE DOWNLINK SPEED UNLESS YOU CHANGE GPS SAME TIME INCREMENT AMOUNT FROM .125
                    if (time.time() - last_downlink_send) > 0:  # Downlink should only be sent at 8hz
                        print("Time since last send: ", time.time() - last_downlink_send)
                        telemetry_downlink.send_data(data, status_bits)
                        last_downlink_send = time.time()
            except Exception as e:
                print("Error sending data to ground station " + str(e))

            try:
                if telemetry_downlink.ser is not None:
                    read_val = telemetry_downlink.read_data()

                    if read_val == 1:
                        # Start go pro 1
                        print("Trying to start GoPro 1")
                        go_pro_1_cam_servo.activate_camera()
                        if flight_status.go_pro_1_on:
                            flight_status.go_pro_1_on = False
                        else:
                            flight_status.go_pro_1_on = True

                    elif read_val == 2:
                        # TELL SRAD2 TO TURN GOPRO2 ON
                        buddy_comm.send(2)
                    elif read_val == 3:
                        # TELL SRAD2 TO TURN GOPRO3 ON
                        buddy_comm.send(3)
                    elif read_val == "RDY":
                        pass
                        # TELL SRAD2 TO BE READY
                    elif read_val == "OVRD":
                        override_mode = True

                    elif read_val == "DSRM" and (flight_status.current_stage() == Stage.PRE_FLIGHT or override_mode):
                        # Doing disarm procedure
                        print("Disarming: ", read_val, "is override mode: ", override_mode, "stage: ",
                              flight_status.current_stage_name())

                        # TELL SRAD2 TO DISARM
                        buddy_comm.send(1)

                        # Disable parachute deployment systems
                        disarmed = True  # Also affect status bits
                        disarmed_time = time.time()  # To wait a bit before shutting down

                        # Turn off all cameras
                        go_pro_1_cam_servo.activate_camera()  # Turns off the camera
                        flight_status.go_pro_1_on = False
                        camera.stop_recording()  # Stops the pi camera

            except Exception as e:
                print("Error reading/using data from ground station " + str(e))

            try:
                # Log the data to a csv file happens at 16hz
                telemetry_logger.log_data(data)
            except:
                print("Error logging data")

            try:
                if (time.time() - last_flight_status_update) > 0.1:  # Flight_status should only be updated at 8hz
                    print("Time since last flight status update should be .125...: ",
                          time.time() - last_flight_status_update)
                    flight_status.new_telemetry(data)
                    last_flight_status_update = time.time()
            except:
                print("Error updating flight status")

            """
            Doing stuff based on messages received from SRAD2
            """
            bc_messages = buddy_comm.get_messages()
            if 0 in bc_messages:
                flight_status.payload_deployed = True
                if bc_messages.count(0) > 1:
                    print("Payload arm retracted")
                print("(buddy) Payload deployed")
            if 1 in bc_messages:
                print("(buddy) SRAD2 is armed and flight ready")
                flight_status.srad2_ready = True
            if 2 in bc_messages:
                flight_status.go_pro_2_on = True
                print("(buddy) GoPro 2 on")
            if 3 in bc_messages:
                flight_status.go_pro_3_on = True
                print("(buddy) GoPro 3 on")

            if led_controller is not None:
                led_controller.update_lights()

            """
            For single threaded temporal handling without using time.sleep() or another thread
            """
            buzzer.update()
            drogue_chute.update()
            main_chute.update()
            go_pro_1_cam_servo.update()

            """
            Stage change handling
            """

            if flight_status.current_stage().value >= Stage.IN_FLIGHT.value:  # If we have taken off, then start recording
                if not camera.recording:
                    camera.start_recording()
            if flight_status.current_stage() == Stage.DESCENT and not buddy_comm.has_sent(0):
                buddy_comm.send(0)  # Tell SRAD2 that we have reached apogee
            if flight_status.current_stage() == Stage.DESCENT and not drogue_chute.deployed and not disarmed:
                print("DROGUE DEPLOYED")
                drogue_chute.deploy()
                drogue_deployed = True
            if flight_status.current_stage() == Stage.DESCENT and flight_status.get_median_altitude_from_last_second() < MAIN_CHUTE_DEPLOY_ALT and not main_chute.deployed and not disarmed:
                print("MAIN DEPLOY")
                main_chute.deploy()
                main_deployed = True

            # Emergency main chute deployment
            if flight_status.drogue_failure and not main_chute.deployed and not disarmed and flight_status.current_stage() == Stage.DESCENT:
                print("Emergency main deploy")
                main_chute.deploy()
                main_deployed = True

            """
            Shutting down the pi (5 seconds after receiving disarm command)
            """
            if disarmed and (time.time() - disarmed_time) > 5:
                print("Final disarming stuff happening")
                call(['shutdown', '-h', 'now'], shell=False)
                exit(1)

        except Exception as e:
            print(
                "\n\n     %%%%%MAIN ERROR -- No error should be caught by this, errors should be handled closer to the exception: " + str(
                    e) + "%%%%%%%\n\n")


if __name__ == '__main__':
    main()
    # alt_bat_test()
