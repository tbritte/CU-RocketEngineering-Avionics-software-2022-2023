import time
import numpy as np
import math
import serial
import Adafruit_BMP.BMP085 as BMP085  # Pressure sensor
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX  # Accelerometer
import adafruit_lis3mdl  # Magnetometer

MAX_GPS_READ_LINES = 100

GPS_QUALITY = {0: "Invalid",
               1: "GPS fix (SPS)",
               2: "DGPS fix"}


class ExtTelemetryHandler:
    def __init__(self):
        self.gps = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0)
        self.old_gps_data = [0, 0, 0, 0, 0, 0]

        self.gps_buffer = ""

        self.BMP180 = BMP085.BMP085(busnum=1)
        print("Calibrating a base_altitude...")
        self.base_altitude = sum([self.get_BMP_data()[0] for _ in range(64)]) / 64
        print("Base altitude is: " + str(self.base_altitude) + " meters")
        self.old_bmp_data = None

        self.i2c = board.I2C()
        try:
            self.lsm6dsox = LSM6DSOX(self.i2c)
        except ValueError:
            print("\n\nAccelerometer not found, please check wiring!\n\n")
            self.lsm6dsox = None

        # Try to find the magnetometer with address 0x1C first, if that fails, try 0x1E
        # This is because the magnetometer has two possible addresses and the default is 0x1C
        try:
            print("Trying to find magnetometer with address 0x1C")
            self.lis3mdl = adafruit_lis3mdl.LIS3MDL(self.i2c)
            print("Magnetometer found with address 0x1C")
        except ValueError:
            try:
                print("Magnetometer not found, trying again with address 0x1e")
                self.lis3mdl = adafruit_lis3mdl.LIS3MDL(self.i2c, address=0x1e)
                print("Magnetometer found with address 0x1E")
            except ValueError:
                print("\n\nMagnetometer not found, please check wiring!\n\n")
                self.lis3mdl = None

    def setup(self):
        pass

    def find_gpgga_in_buffer(self):
        for i in range(len(self.gps_buffer)):
            spot = len(self.gps_buffer) - i - 6
            # looking for the start of the GPGGA message
            if self.gps_buffer[spot:spot+6] == "$GPGGA":
                # print("Found GPGGA message:", spot)
                # Checking if there is a newline after the message
                for j in range(spot, len(self.gps_buffer)):
                    if self.gps_buffer[j] == "\n":
                        # print("Found newline after GPGGA message:", j)
                        return spot
        return None

    def get_gps_data(self):
        # print("Getting GPS data...")
        try:
            self.gps_buffer += self.gps.readline().decode("utf-8")
            if len(self.gps_buffer) > 10000:  # 10000 character limit on buffer, it's arbitrary
                self.gps_buffer = self.gps_buffer[-10000:]
        except UnicodeDecodeError:
            pass
        except:
            pass

        # print("\nbuffer: ", self.gps_buffer, "\n")

        #  Looking through the newest date in the buffer for the GPGGA message
        #  This is the message that contains the GPS data

        spot = self.find_gpgga_in_buffer()

        if spot is not None:
            message = ""
            # Iterating from spot till newline and putting that in the message
            for i in range(spot, len(self.gps_buffer)):
                if self.gps_buffer[i] == "\n":
                    break
                message += self.gps_buffer[i]

            parts = message.split(",")
            try:
                utc_time = ""
                try:
                    utc_time = parts[1]  # hhmmss.sss format (UTC)
                    longitude = float(parts[4])
                    latitude = float(parts[2])
                    alt = float(parts[9])
                    quality = parts[6]
                    sat_num = parts[7]

                    # Using the good data
                    real_data = [longitude, latitude, alt, quality, sat_num, utc_time]
                    self.old_gps_data = real_data  # Save the data to be used if no data comes in one time
                    return real_data

                except ValueError:
                    # Occurs when the GPS is not getting a signal
                    # Updating the old_time if that is there
                    if len(utc_time) > 2:
                        self.old_gps_data[5] = utc_time

            except IndexError:
                print("    Index Error, parts were: " + str(parts), "\n    Data was: " + str(message))
                print("Next line would be: " + self.gps.readline().decode("utf-8"))
                pass
            except TypeError:
                print("    Type Error, parts were: " + str(parts), "\n    Data was: " + str(message))
                print("Next line would be: " + self.gps.readline().decode("utf-8"))
                pass
            except:
                print("     Unknown GPS collection Error --- Line 121")
        return self.old_gps_data  # May have an updated UTC time value

    def get_BMP_data(self):
        # Get the altitude from the BMP180 sensor
        altitude = self.BMP180.read_altitude()
        # Get the pressure from the BMP180 sensor
        pressure = self.BMP180.read_pressure()
        # Get the temperature from the BMP180 sensor
        temperature = self.BMP180.read_temperature()

        return altitude, pressure, temperature

    def get_gyro_data(self):
        try:
            gyro_x, gyro_y, gyro_z = self.lsm6dsox.gyro
        except:
            print("Error getting gyro data")
            gyro_x, gyro_y, gyro_z = 0, 0, 0

        try:
            acl_x, acl_y, acl_z = self.lsm6dsox.acceleration
        except:
            print("Error getting acceleration data")
            acl_x, acl_y, acl_z = 0, 0, 0
        
        try:
            mag_x, mag_y, mag_z = self.lis3mdl.magnetic
        except:
            print("Error getting magnetometer data")
            mag_x, mag_y, mag_z = 0, 0, 0

        return gyro_x, gyro_y, gyro_z, acl_x, acl_y, acl_z, mag_x, mag_y, mag_z

    def get_data(self):
        """
        Gets all the data from the external sensors and returns it in a dictionary
        :return: Dictionary with all the data
        """

        gps_data = self.get_gps_data()

        # print("    ERROR in get GPS")
        # gps_data = None
        if gps_data is not None:
            longitude, latitude, gps_alt, gps_quality, gps_sat_num, utc_time = gps_data
        else:
            # get_gps_data() handles the old gps data, so it is no updated or used here
            print("    No GPS data returned. Could happen if the first GPS read fails and there is no old data")
            longitude, latitude, gps_alt, gps_quality, gps_sat_num, utc_time = 0, 0, 0, 0, 0, 0

        try:

            # Converting the GPS time to a more readable format
            if utc_time != 0:
                utc_time = str(utc_time[:2]) + ":" + str(utc_time[2:4]) + ":" + str(utc_time[4:])


        except TypeError:
            print("    TypeError in GPS data readability conversion... Leaving data in ugly format for now")
        except:
            print("    Non TypeError in GPS data readability conversion... Leaving data in ugly format for now")


        # Get the altitude from the BMP180 sensor
        try:
            BMP_data = self.get_BMP_data()
            self.old_bmp_data = BMP_data
        except:
            print("    ERROR in get BMP")
            BMP_data = self.old_bmp_data

        altitude, bar_pressure, bar_temp = BMP_data
        if self.lsm6dsox is not None and self.lis3mdl is not None:
            gyro_data = self.get_gyro_data()
        else:
            gyro_data = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        gyro_x, gyro_y, gyro_z, acl_x, acl_y, acl_z, mag_x, mag_y, mag_z = gyro_data
        # print("mags", mag_x, mag_y, mag_z)
        heading = math.atan2(mag_y, mag_x) * 180 / math.pi


        # Dealing with < 360 and > 360
        if heading < 0:
            heading += 360
        if heading > 360:
            heading -= 360

        # print("heading = ", heading)

        # The altitude is the difference between the current altitude and the base altitude
        altitude = altitude - self.base_altitude

        data = {"latitude": latitude, "longitude": longitude,
                "gps_altitude": gps_alt, "gps_time": utc_time, "gps_quality": gps_quality, "gps_sat_num": gps_sat_num,
                "altitude": altitude, "bar_pressure": bar_pressure, "bar_temp": bar_temp,
                "gyro_x": gyro_x, "gyro_y": gyro_y, "gyro_z": gyro_z,
                "acl_x": acl_x, "acl_y": acl_y, "acl_z": acl_z, "mag_x": mag_x, "mag_y": mag_y, "mag_z": mag_z}

        return data

    @staticmethod
    def get_data_header_list():

        columns = ['time', 'gps_time', 'state', 'altitude', 'gps_altitude', 'data_pulls', 'bar_pressure',
                   'bar_temp', 'gyro_x', 'gyro_y', 'gyro_z', 'acl_x', 'acl_y', 'acl_z', 'mag_x', 'mag_y', 'mag_z',
                   'latitude', 'longitude', 'gps_quality', 'gps_sat_num',
                   'cputemp']
        return columns