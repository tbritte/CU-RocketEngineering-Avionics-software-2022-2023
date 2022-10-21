from enum import Enum
from statistics import median

class Stage(Enum):
    PRE_FLIGHT = 1
    IN_FLIGHT = 2
    DESCENT = 3
    ON_GROUND = 4

class FlightStatus:
    def __init__(self, base_altitude: float = 0):
        self.stage = Stage.PRE_FLIGHT
        self.altitude_list = [] # 64 is the number of altitude samples to leave in memory
        self.base_altitude = base_altitude
    
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
        return lm - fm < self.base_altitude + 10

    def new_telemetry(self, telemetry: dict) -> None:
        """Updates the flight status based on the new telemetry.

        Args:
            telemetry (dict): Current telemetry from the Sense Hat.
        """
        self.add_altitude(telemetry['altitude'])
        
        if len(self.altitude_list) >= 64:
            if self.stage.value == Stage.PRE_FLIGHT.value and self.check_liftoff():
                self.stage = Stage.IN_FLIGHT
            elif self.stage.value == Stage.IN_FLIGHT.value and self.check_apogee():
                self.stage = Stage.DESCENT
            elif Stage >= self.stage.value == Stage.DESCENT.value and self.check_landed():
                self.stage = Stage.ON_GROUND
