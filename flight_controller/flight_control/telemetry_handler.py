import time
import numpy as np

from sense_emu import SenseHat

class TelemetryHandler():
    def __init__(self):
        self.sense = SenseHat()
        
        self.pressure_arr = [self.sense.get_pressure() for i in range(8)]
        self.base_pressure = 0
        self.base_altitude = 0
    
    def setup(self) -> None:
        """Setup the telemetry handler.
        """
        
        base_pressure_arr = []
        last_data_pull = time.time()
        while len(base_pressure_arr) < 64:
            if time.time() - last_data_pull > 0.0625:
                last_data_pull = time.time()
                base_pressure_arr.append(self.sense.get_pressure())
        
        self.base_pressure = np.mean(base_pressure_arr)
        self.base_altitude = self.calculate_altitude(base_pressure_arr)


    def get_data(self) -> dict:
        """Gets all data from the Sense Hat Raspberry Pi Accessory and returns it as a dictionary.

        Data Info:
        humidity: float - Percent of relative humidity.
        pressure: float - Atmospheric pressure in millibars.
        humidity_temp: float - Temperature in degrees Celsius determined by Humidity.
        pressure_temp: float - Temperature in Celsius as determined by the pressure levels.
        temp: float - Average temperature in Celsius taken from the pressure and humidity temp values.
        north: float - Magnetic north in degrees.
        orientation: dict - Orientation of the Sense Hat in degrees. (keys: pitch, roll, yaw)
        raw_magnetometer: dict - Raw magnetometer data. (WILL BE REPLACED BY A FAR MORE ACCURATE ONE IN THE FUTURE BY KYLE JONES)
        raw_accelerometer: dict - Raw accelerometer data, is the acceleration intensity of the axis in Gs. (keys: x, y, z)

        Returns:
            dict: A dictionary containing all data from the Sense Hat.
        """

        humidity = self.sense.get_humidity()
        pressure = self.sense.get_pressure()
        
        self.add_pressure(pressure)
        altitude = self.current_altitude()
        
        humidity_temp = self.sense.get_temperature_from_humidity()
        pressure_temp = self.sense.get_temperature_from_pressure()
        # Averages humidity_temp and pressure_temp
        temp = (humidity_temp + pressure_temp) / 2
        
        orientation = self.sense.get_orientation_degrees()
        raw_accelerometer = self.sense.get_accelerometer_raw()
        
        north = self.sense.get_compass()
        raw_magnetometer = self.sense.get_compass_raw()
        
        data = {'humidity': humidity, 'pressure': pressure, 'altitude': altitude, 'humidity_temp': humidity_temp, 'pressure_temp': pressure_temp, 'temp': temp,
                'orientation': orientation, 'raw_accelerometer': raw_accelerometer, 'north': north, 'raw_magnetometer': raw_magnetometer}

        return data

    def print_data(self):
        """Prints out all data from the Sense Hat.
        """
        
        data = self.get_data()
        for key, value in data.items():
            print(f"{key}: {value}")
    
    def add_pressure(self, pressure: float):
        """Adds a pressure value to the pressure array.

        Args:
            pressure (float): The pressure to add to the array.
        """
        self.pressure_arr.append(pressure)
        self.pressure_arr.pop(0)
    
    def calculate_altitude(self, pressure_arr: list, seaLevelPressure: float = 1013.25) -> float:
        """Calculates the altitude of the rocket based on the pressure.

        Args:
            pressure_arr (list): The current air pressure, in list format.
            seaLevelPressure (float, optional): The pressure at sea level. Defaults to 1013.25.

        Returns:
            float: The altitude of the rocket in meters.
        """
        average_pressure = np.mean(pressure_arr)
        altitude = 44330 * (1.0 - pow(average_pressure / seaLevelPressure, 1 / 5.255)) # Used formula from https://github.com/adafruit/Adafruit_BMP280_Library
        return altitude - self.base_altitude
    
    def current_altitude(self) -> float:
        """Returns the current altitude of the rocket.

        Returns:
            float: The current altitude of the rocket.
        """
        return self.calculate_altitude(self.pressure_arr)