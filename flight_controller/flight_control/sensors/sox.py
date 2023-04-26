"""
For the LSM6DSOX+LIS3MDL board for Magnetometer, Gyroscope, and Accelerometer
"""

import time
from .sensor import Sensor
import board
import busio
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX  # Accelerometer
import adafruit_lis3mdl  # Magnetometer

class SOX(Sensor):
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor_name = "SOX"
        self.lsm6dsox = None
        self.lis3mdl = None
        super().__init__(self.sensor_name)

    def setup(self):
        """
        Tries to find the accelerometer and magnetometer on the I2C bus
        If it fails, it will print an error message and set the variable to None
        Called when the class is initialized or when there is bad data
        """
        try:
            self.lsm6dsox = LSM6DSOX(self.i2c)
            self.functional = True
            print("    Accelerometer setup successful")
        except ValueError:
            print("    Accelerometer not found, please check wiring!")
            self.lsm6dsox = None

        # Try to find the magnetometer with address 0x1C first, if that fails, try 0x1E
        # This is because the magnetometer has two possible addresses and the default is 0x1C
        try:
            print("    Trying to find magnetometer with address 0x1C")
            self.lis3mdl = adafruit_lis3mdl.LIS3MDL(self.i2c)
            print("    Magnetometer found with address 0x1C")
        except ValueError:
            try:
                print("    Magnetometer not found, trying again with address 0x1e")
                self.lis3mdl = adafruit_lis3mdl.LIS3MDL(self.i2c, address=0x1e)
                print("    Magnetometer found with address 0x1E")
            except ValueError:
                print("    Magnetometer not found, please check wiring!")
                self.lis3mdl = None

    def get_new_data(self):
        """
        Gets the new data from the accelerometer and magnetometer
        Returns the data as a tuple
        """
        gyro = [0, 0, 0]
        acceleration = [0, 0, 0]
        magnetic_field = [0, 0, 0]

        if self.lsm6dsox is not None and self.lis3mdl is not None:
            try:
                try:
                    # Get the acceleration from the LSM6DSOX sensor
                    acceleration = self.lsm6dsox.acceleration
                except Exception as e:
                    print("Error getting acceleration: {}".format(e))

                try:
                    # Get the gyro from the LSM6DSOX sensor
                    gyro = self.lsm6dsox.gyro
                except Exception as e:
                    print("Error getting gyro: {}".format(e))

                try:
                    # Get the magnetic field from the LIS3MDL sensor
                    magnetic_field = self.lis3mdl.magnetic
                except Exception as e:
                    print("Error getting magnetic field: {}".format(e))

                return acceleration, gyro, magnetic_field
            except OSError:
                print("OSError getting SOX data")
                return None
        else:
            return gyro + acceleration + magnetic_field