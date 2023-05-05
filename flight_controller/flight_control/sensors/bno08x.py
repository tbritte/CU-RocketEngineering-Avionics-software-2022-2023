from .sensor import Sensor
import time

from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
)

from adafruit_bno08x.i2c import BNO08X_I2C
import board
import busio

class BNO08X(Sensor):
    def __init__(self):
        self.sensor_name = "BNO08X"
        self.bno = None
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        super().__init__(self.sensor_name)

    def setup(self):
        try:
            self.bno = BNO08X_I2C(self.i2c)
            self.bno.initialize()
            self.functional = True
            try:
                self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
            except Exception as e:
                print("    Error enabling accelerometer: {}".format(e))
                self.functional = False

            try:
                self.bno.enable_feature(BNO_REPORT_GYROSCOPE)
            except Exception as e:
                print("    Error enabling gyroscope: {}".format(e))
                self.functional = False

            try:
                self.bno.enable_feature(BNO_REPORT_MAGNETOMETER)
            except Exception as e:
                print("    Error enabling magnetometer: {}".format(e))
                self.functional = False

            if self.functional:
                print("    BNO08X setup successful")
            else:
                print("    BNO08X setup failed")

        except ValueError:
            print("    BNO08X not found, please check wiring! (Value Error)")
            self.bno = None

        except Exception as e:
            print("    BNO08X not found, please check wiring!, {}".format(e))
            self.bno = None

    def get_new_data(self):
        # print("\n\nGetting new BNO data\n\n")
        if self.bno is not None:
            try:
                time_before_just_gyro = time.monotonic()
                gyro_x, gyro_y, gyro_z = self.bno.gyro
                # print("   Time to get just gyro data: ", time.monotonic() - time_before_just_gyro)
                time_before_just_mag = time.monotonic()
                mag_x, mag_y, mag_z = self.bno.magnetic
                # print("   Time to get just mag data: ", time.monotonic() - time_before_just_mag)
                time_before_just_acl = time.monotonic()
                acl_x, acl_y, acl_z = self.bno.acceleration
                # print("   Time to get just acl data: ", time.monotonic() - time_before_just_acl)

            except Exception as e:
                print("Error getting BNO055 data exception is: ", e)
                gyro_x, gyro_y, gyro_z = 0, 0, 0
                mag_x, mag_y, mag_z = 0, 0, 0
                acl_x, acl_y, acl_z = 0, 0, 0
        else:
            print("BNO is None, setting everything to zero")
            gyro_x, gyro_y, gyro_z = 0, 0, 0
            mag_x, mag_y, mag_z = 0, 0, 0
            acl_x, acl_y, acl_z = 0, 0, 0
        # print("(BNO) DATA RETURNED", gyro_x, gyro_y, gyro_z, acl_x, acl_y, acl_z, mag_x, mag_y, mag_z)
        return gyro_x, gyro_y, gyro_z, acl_x, acl_y, acl_z, mag_x, mag_y, mag_z
