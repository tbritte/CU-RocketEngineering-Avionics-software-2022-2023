from enum import Enum

class Stage(Enum):
    PRE_FLIGHT = 1
    LIFTOFF = 2
    IN_FLIGHT = 3
    APOGEE = 4
    DESCENT = 5
    POST_FLIGHT = 6


class FlightStatus:
    def __init__(self):
        self.stage = Stage.pre_flight
        self.altitude_list = [0 for i in range(10)]
        self.acceleration = 0
    
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
        self.altitude_list.pop(0)

    def new_telemetry(self, telemetry: dict) -> None:
        """Updates the flight status based on the new telemetry.

        Args:
            telemetry (dict): Current telemetry from the Sense Hat.
        """
        self.add_altitude(telemetry['altitude'])
        self.acceleration = telemetry['raw_accelerometer']
        
        if (sum(self.altitude_list[0:5]) / 5) > (sum(self.altitude_list[5:10]) / 5) and self.stage.value <= Stage.liftoff.value:
            self.stage = Stage.in_flight
        elif (sum(self.altitude_list[0:5]) / 5) < (sum(self.altitude_list[5:10]) / 5) and self.stage.value <= Stage.apogee.value:
            self.stage = Stage.descent
        