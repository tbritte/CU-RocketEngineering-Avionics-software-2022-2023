from enum import Enum
from statistics import median


class Stage(Enum):
    UNARMED = 0
    PRE_FLIGHT = 1
    IN_FLIGHT = 2
    DESCENT = 3
    ON_GROUND = 4


class FlightStatus:
    def __init__(self, buzzer):
        self.stage = Stage.UNARMED
        self.altitude_list = []
        self.vertical_acceleration_list = []

        self.buzzer = buzzer

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
        if len(self.altitude_list) == 65:
            self.altitude_list.pop(0)
        elif len(self.altitude_list) > 65:
            print('CRITICAL ERROR: Too many altitude variables stored')

    def add_vertical_acceleration(self, vertical_acceleration: float) -> None:
        """Adds a vertical acceleration to the vertical acceleration list.

        Args:
            vertical_acceleration (float): The vertical acceleration to add to the list.
        """
        self.vertical_acceleration_list.append(vertical_acceleration)
        if len(self.vertical_acceleration_list) == 65:
            self.vertical_acceleration_list.pop(0)
        elif len(self.vertical_acceleration_list) > 65:
            print('CRITICAL ERROR: Too many vertical acceleration variables stored')

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
        Determines if the rocket has liftoff. Using accleration data
        :return: bool: True if the rocket has liftoff, False otherwise.
        """
        # Newest 8 samples (1 seconds)
        median_vertical_accleration_one_second = median(self.vertical_acceleration_list[64 - 8:])

        if median_vertical_accleration_one_second > (9.8 * 3):  # 3g
            return True
        else:
            return False


    # IMPORTANT: SHOULD WE USE LESS OLDER SAMPLES TO DETECT APOGEE SOONER???
    def check_apogee(self) -> bool:  # Checks if the rocket is past the apogee
        """Determines if the rocket has passed the apogee.
        
        If the median of the last second of altitude values is less than the
        median of the previous values, declare apogee has passed
        
        Returns:
            bool: True if the rocket has passed the apogee, False otherwise.
        """
        lm = median(self.altitude_list[64 - 8:])  # Newest 8 samples (1 seconds)
        fm = median(self.altitude_list[64 - 16:64 - 8])  # Second newest 8 samples 1 to 2 second ago)
        return lm < fm

    def check_landed(self) -> bool:
        """Determines if the rocket has landed.

        Returns:
            bool: True if the rocket has landed, False otherwise.
        """
        lm = median(self.altitude_list[64 - 8:])  # Newest 8 samples (.5 seconds)
        return lm < 10  # Altitude is already relative to base altitude. Checking if we are below 10 meters above base altitude

    def new_telemetry(self, telemetry: dict) -> None:
        """Updates the flight status based on the new telemetry.

        Args:
            telemetry (dict): Current telemetry from the Sense Hat.
        """
        self.add_altitude(telemetry['altitude'])
        self.add_vertical_acceleration(telemetry['acl_z'])

        if len(self.altitude_list) >= 64:
            if self.stage.value == Stage.UNARMED.value:  # and self.check_armed():
                self.stage = Stage.PRE_FLIGHT
                self.buzzer.armed_beeps()  # Plays 20 quick beeps
            elif self.stage.value == Stage.PRE_FLIGHT.value and self.check_liftoff():
                self.stage = Stage.IN_FLIGHT
            elif self.stage.value == Stage.IN_FLIGHT.value and self.check_apogee():
                self.stage = Stage.DESCENT
            elif self.stage.value == Stage.DESCENT.value and self.check_landed():
                self.stage = Stage.ON_GROUND
        else:
            print("Need more altitude, collecting...", len(self.altitude_list))
