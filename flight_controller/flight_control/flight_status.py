import statistics
from enum import Enum
from statistics import median
import time

"""
Mach lock
"""

class Stage(Enum):
    UNARMED = 0  # No longer used
    PRE_FLIGHT = 1
    IN_FLIGHT = 2
    DESCENT = 3
    ON_GROUND = 4


class FlightStatus:
    def __init__(self, buzzer):
        self.stage = Stage.PRE_FLIGHT  # Starting stage is pre-flight
        self.altitude_list = []
        self.vertical_acceleration_list = []  # 8 acceleration values are saved (1 second of data)

        self.buzzer = buzzer

        self.time_of_apogee = 0

        self.drogue_failure = False
        self.time_fired_backup_drogue = 0  # When the backup drogue was fired (only happens if drogue failure)

        self.payload_deployed = False
        self.go_pro_1_on = False
        self.go_pro_2_on = False
        self.go_pro_3_on = False
        self.pi_cam2_on = False
        self.srad2_ready = False

        self.has_hit_floor_alt = False  # Has the rocket been to at least 2000 ft (609.9 meters)


    def collect_status_bits(self, data, drouge_deployed, main_deployed, disarmed, backup_drogue_deployed,
                            emergency_main_deployed):
        try:
            e_spin = sum(abs(data["gyro_x"]) + abs(data["gyro_y"]) + abs(data["gyro_z"])) > 720
        except TypeError:
            e_spin = False

        status_bits = {"active aero": False,
                       "excessive spin": e_spin,
                       "excessive vibration": data["acl_x"] > 100 or data["acl_y"] > 100 or data["acl_z"] > 100,
                       "srad2 ready": self.srad2_ready,
                       "disarmed": disarmed,
                       "launch detected": self.stage.value > Stage.PRE_FLIGHT.value,
                       "apogee detected": self.stage.value > Stage.IN_FLIGHT.value,
                       "drogue deployed": drouge_deployed,
                       "main deployed": main_deployed,
                       "touchdown": self.stage.value > Stage.DESCENT.value,
                       "payload deployed": self.payload_deployed,
                       "backup drogue": backup_drogue_deployed,
                        "emergency main": emergency_main_deployed,
                        "Go Pro 1 On": self.go_pro_1_on,
                        "Go Pro 2 On": self.go_pro_2_on,
                        "Go Pro 3 On": self.go_pro_3_on,
                       }
        # print(status_bits)
        return status_bits


    def current_stage(self) -> Stage:
        """Returns the current stage of the rocket.

        Returns:
            Stage: The current stage of the rocket.
        """
        return self.stage

    def current_stage_name(self) -> str:
        """Returns the current stage of the rocket as a string.

        Returns:
            str: The current stage of the rocket as a string.
        """
        return self.stage.name

    def add_altitude(self, altitude: float) -> None:
        """Adds an altitude to the altitude list and sets the current altitude.
        
        Args:
            altitude (float): The altitude to add to the list.
        """
        self.altitude_list.append(altitude)
        if len(self.altitude_list) == 65:  # 64 samples (8 seconds of data)
            self.altitude_list.pop(0)
        elif len(self.altitude_list) > 65:
            print('CRITICAL ERROR: Too many altitude variables stored')

    def get_median_altitude_from_last_second(self):
        """
        Returns the median of the last second of altitude values
        :return:  median of the last second of altitude values
        """
        try:
            return median(self.altitude_list[-8:])
        except statistics.StatisticsError:
            print("No altitude data")
            return 0

    def add_vertical_acceleration(self, vertical_acceleration: float) -> None:
        """Adds a vertical acceleration to the vertical acceleration list.

        Args:
            vertical_acceleration (float): The vertical acceleration to add to the list.
        """
        self.vertical_acceleration_list.append(vertical_acceleration)
        if len(self.vertical_acceleration_list) > 8:  # 8 samples (1 second of data)
            self.vertical_acceleration_list.pop(0)
        elif len(self.vertical_acceleration_list) > 8:
            print('CRITICAL ERROR: Too many vertical acceleration variables stored')

        if sum(self.vertical_acceleration_list) == 0:
            print("Bad vertical acceleration dat")

    # def check_armed(self) -> bool:
    #     """Determines if the rocket is armed.
    #     """
    #     for event in self.sense.stick.get_events():
    #         if event.action == "pressed":
    #             if event.direction == "up":
    #                 return True
    #     return False

    def check_liftoff(self) -> bool:
        """
        Determines if the rocket has liftoff. Using acceleration data
        :return: bool: True if the rocket has liftoff, False otherwise.
        """
        # Newest 8 samples (1 seconds)
        median_vertical_acceleration = median(self.vertical_acceleration_list)

        if median_vertical_acceleration > (9.8 * 3):  # 3g as the median vertical acceleration from the last .5 seconds
            return True
        else:
            return False


    # IMPORTANT: SHOULD WE USE LESS OLDER SAMPLES TO DETECT APOGEE SOONER???
    def check_apogee(self) -> bool:  # Checks if the rocket is past the apogee
        """Determines if the rocket has passed the apogee.
        
        If the median of the last second of altitude values is less than the
        median of the previous values, declare apogee has passed

        We also must pass the altitude floor to ensure we are not detecting apogee way too early.
        
        Returns:
            bool: True if the rocket has passed the apogee, False otherwise.
        """
        if not self.has_hit_floor_alt:
            return False

        one_second = median(self.altitude_list[64 - 8:])  # Newest 8 samples (1 seconds)
        two_second = median(self.altitude_list[64 - 16:64 - 8])  # Second newest 8 samples 1 to 2 second ago)
        three_second = median(self.altitude_list[64 - 24:64 - 16])  # Third newest 8 samples (2 to 3 seconds ago)
        # v_acl = median(self.vertical_acceleration_list)  # Last 4 samples (0.5 seconds)
        # Vertical acceleration should be close to gravity (1g) because the engine should be off

        # Taking the average of the two_second and three_second medians for sooner apogee detection compared to
        # making sure one_second is less than both of them.
        return one_second < (two_second + three_second) / 2

    def check_landed(self) -> bool:
        """Determines if the rocket has landed.

        Returns:
            bool: True if the rocket has landed, False otherwise.
        """
        lm = median(self.altitude_list)  # Entire list, 8 seconds, there is no rush to detect landing
        v_acl = median(self.vertical_acceleration_list)  # Last 4 samples (0.5 seconds)
        # Altitude is already relative to base altitude. Checking if we are below 10 meters above base altitude
        # and if the vertical acceleration is near gravity (1g +- 0.5g)
        return lm < 10 and abs(v_acl - 9.8) < .5

    def too_fast_descent(self) -> bool:
        """
        Determines if the rocket is descending too fast which implies that the drogue chute failed
        Returns false if it's been less than 3 seconds since apogee to give the drogue chute time to deploy/unravel
        This is to deploy the main chute or to try deploying the drogue again to avoid waiting till we are too fast

        The too fast speed is 50 m/s
        """

        # Checking that it has been at least 3 seconds since apogee to give the drogue chute time to deploy
        if (time.time() - self.time_of_apogee) > 3:
            # using the last 8 samples of altitude data (m)
            current_altitude_m = self.altitude_list[-1]
            altitude_one_second_ago_m = self.altitude_list[-8]
            altitude_two_second_ago_m = self.altitude_list[-16]
            altitude_three_second_ago_m = self.altitude_list[-24]

            change_in_alt_from_one_second_ago = altitude_one_second_ago_m - current_altitude_m
            change_in_alt_from_two_second_ago = altitude_two_second_ago_m - altitude_one_second_ago_m
            change_in_alt_from_three_second_ago = altitude_three_second_ago_m - altitude_two_second_ago_m

            if change_in_alt_from_one_second_ago > 50:  # 50 m/s
                # We are going down too fast, but let's make sure the velocity is increasing from previous seconds
                # We shouldn't expect the velocity to be increasing at 9.8 m/s^2 due to drag, so we will check for 8 m/s^2

                # WARNING, 8 m/s^2 is a guess, it could definitely be a lower value in the case of a partial chute deployment

                if change_in_alt_from_one_second_ago > change_in_alt_from_two_second_ago + 8:  # Gained 8 m/s in 1 second i.e. 8 m/s^2
                    if change_in_alt_from_two_second_ago > change_in_alt_from_three_second_ago + 8:  # Gained 8 m/s in 1 second i.e. 8 m/s^2
                        return True
        return False



    def new_telemetry(self, telemetry: dict) -> None:
        """Updates the flight status based on the new telemetry.

        Args:
            telemetry (dict): Current telemetry from the Sense Hat.
        """
        self.add_altitude(telemetry['altitude'])
        self.add_vertical_acceleration(abs(telemetry['acl_x']))

        if len(self.altitude_list) >= 64:
            # if self.stage.value == Stage.UNARMED.value:  # and self.check_armed():
            #     self.stage = Stage.PRE_FLIGHT
            #     self.buzzer.armed_beeps()  # Plays 20 quick beeps
            if self.stage.value == Stage.PRE_FLIGHT.value and self.check_liftoff():
                self.stage = Stage.IN_FLIGHT
            elif self.stage.value == Stage.IN_FLIGHT.value and self.check_apogee():
                self.time_of_apogee = time.time()
                self.stage = Stage.DESCENT
            elif self.stage.value == Stage.DESCENT.value and self.check_landed():
                self.stage = Stage.ON_GROUND

            # If we are moving too fast after apogee, we assume the drogue chute failed
            if self.stage.value == Stage.DESCENT.value and self.too_fast_descent():
                self.drogue_failure = True

            # Checking if we have passed 2000 ft
            if not self.has_hit_floor_alt and self.get_median_altitude_from_last_second() > 609.6:
                print("(flight status) we have passed 2000ft (609.6 meters)")
                self.has_hit_floor_alt = True






        else:
            print("Flight Status doing its own altitude calibration, collecting...", len(self.altitude_list))
