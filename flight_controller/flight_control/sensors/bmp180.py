from .sensor import Sensor
import Adafruit_BMP.BMP085 as BMP085  # Pressure sensor
import numpy as np
import time

class BMP180(Sensor):
    def __init__(self):
        super().__init__()
        self.base_alt = None  # in meters above sea level
        self.sensor_name = "BMP180"
        self.bmp180 = None

    def setup(self):
        try:
            self.bmp180 = BMP085.BMP085(busnum=1)
            self.calibrate_initial_altitude()
        except:
            print("     BMP180 not found, check wiring")
            self.bmp180 = None
            return

    def calibrate_initial_altitude(self):
        """
        Calibrates the initial altitude of the rocket by taking the median of 64 altitude readings
        Sets self.base_altitude to the median altitude
        """
        alts = []
        for _ in range(64):
            alts.append(self.get_new_data()[0])
            time.sleep(0.01)

        # Getting the median altitude to deal with outliers
        self.base_alt = np.median(alts)
        print("     BMP180 calibrated to {} meters".format(self.base_alt))

    def get_new_data(self):
        if self.bmp180 is not None:
            try:
                # Get the altitude from the BMP180 sensor
                altitude = self.bmp180.read_altitude()
                # Get the pressure from the BMP180 sensor
                pressure = self.bmp180.read_pressure()
                # Get the temperature from the BMP180 sensor
                temperature = self.bmp180.read_temperature()
                return altitude, pressure, temperature
            except OSError:
                print("OSError getting BMP data")