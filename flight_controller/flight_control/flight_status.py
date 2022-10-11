from enum import Enum
from statistics import median

class Stage(Enum):
    PRE_FLIGHT = 1
    LIFTOFF = 2
    IN_FLIGHT = 3
    APOGEE = 4
    DESCENT = 5
    ON_GROUND = 6

class FlightStatus:
    def __init__(self):
        self.stage = Stage.PRE_FLIGHT
        self.altitude_list = [0 for i in range(64)] # 64 is the number of altitude samples to leave in memory
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
    
    def check_liftoff(self) -> bool:
        """Determines if the rocket has liftoff.

        Returns:
            bool: True if the rocket has liftoff, False otherwise.
        """
        lm = median(self.altitude_list[64-8:])  # Newest 8 samples (.5 seconds)
        fm = median(self.altitude_list[:64-8])  # Oldest 56 samples (3.5 seconds)
        return lm - fm > 10
    
    
    # IMPORTANT: SHOULD WE USE LESS OLDER SAMPLES TO DETECT APOGEE SOONER???
    def check_apogee(self) -> bool:  # Checks if the rocket is past the apogee
        """Determines if the rocket has passed the apogee.
        
        If the median of the last second of altitude values is less than the
        median of the previous values, declare apogee has passed
        
        Returns:
            bool: True if the rocket has passed the apogee, False otherwise.
        """
        lm = median(self.altitude_list[64-8:])  # Newest 8 samples (.5 seconds)
        fm = median(self.altitude_list[:64-8])  # Oldest 56 samples (3.5 seconds)
        return lm < fm
    
    def check_landed(self) -> bool:
        """Determines if the rocket has landed.

        Returns:
            bool: True if the rocket has landed, False otherwise.
        """
        lm = median(self.altitude_list[64-8:])  # Newest 8 samples (.5 seconds)
        fm = median(self.altitude_list[:64-8])  # Oldest 56 samples (3.5 seconds)
        return lm - fm < 3

    def new_telemetry(self, telemetry: dict) -> None:
        """Updates the flight status based on the new telemetry.

        Args:
            telemetry (dict): Current telemetry from the Sense Hat.
        """
        self.add_altitude(telemetry['altitude'])
        self.acceleration = telemetry['raw_accelerometer']
        
        if self.stage.value == Stage.PRE_FLIGHT.value and self.check_liftoff():
            self.stage = Stage.IN_FLIGHT
        elif self.stage.value <= Stage.IN_FLIGHT and self.check_apogee():
            self.stage = Stage.DESCENT
        elif self.stage.value <= Stage.DESCENT and self.check_landed():
            self.stage = Stage.ON_GROUND
