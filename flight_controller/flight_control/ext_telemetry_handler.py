import time
import numpy as np
import serial
import Adafruit_BMP.BMP085 as BMP085

MAX_GPS_READ_LINES = 100

GPS_QUALITY = {0: "Invalid",
               1: "GPS fix (SPS)",
               2: "DGPS fix"}


class ExtTelemetryHandler:
    def __init__(self):
        self.gps = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0)
        self.old_gps_data = None

        self.BMP180 = BMP085.BMP085(busnum=1)
        print("Calibrating a base_altitude...")
        self.base_altitude = sum([self.get_BMP_data()[0] for _ in range(64)]) / 64
        print("Base altitude is: " + str(self.base_altitude))

    def setup(self):
        pass

    def get_gps_data(self):
        # print("Getting GPS data...")
        message = None
        data = None
        tries = 0
        while message != "$GPGGA" and tries < MAX_GPS_READ_LINES:  # GPGGA is the message type for GPS data (Global Positioning System)
            tries += 1
            data = self.gps.readline().decode("utf-8")
            message = data[0:6]

        # print("Found a GPS message")

        if tries < MAX_GPS_READ_LINES:  # Actually found the data
            parts = data.split(",")
            try:
                longitude = parts[4]
                latitude = parts[2]
                alt = parts[9]
                quality = parts[6]
                sat_num = parts[7]
                utc_time = parts[1]  # hhmmss.sss format (UTC)

                print("lat = " + str(latitude) + ", lon = " + str(longitude),
                      "alt = " + str(alt) + " meters",
                      "quality = " + GPS_QUALITY[int(quality)] + ", satellites = " + str(sat_num))

                # GPS altitude is true altitude (above sea level)

                real_data = [longitude, latitude, alt, quality, sat_num, utc_time]
                self.old_gps_data = real_data  # Save the data to be used if no data comes in one time
                return real_data
            except IndexError:
                print("Index Error, parts was: " + str(parts))
                return self.old_gps_data
        else:
            return self.old_gps_data

    def get_BMP_data(self):
        # Get the altitude from the BMP180 sensor
        altitude = self.BMP180.read_altitude()
        # Get the pressure from the BMP180 sensor
        pressure = self.BMP180.read_pressure()
        # Get the temperature from the BMP180 sensor
        temperature = self.BMP180.read_temperature()

        return altitude, pressure, temperature

    def get_data(self):
        try:
            gps_data = self.get_gps_data()
        except:
            print("ERROR in get GPS")
            gps_data = None
        if gps_data is not None:
            longitude, latitude, gps_alt, gps_quality, gps_sat_num, utc_time = gps_data
        else:
            print("No GPS data returned")
            longitude, latitude, gps_alt, gps_quality, gps_sat_num, utc_time = 0, 0, 0, 0, 0, 0

        try:
            BMP_data = self.get_BMP_data()
        except:
            print("ERROR in get BMP")
            BMP_data = None


        altitude, bar_pressure, bar_temp = BMP_data

        # The altitude is the difference between the current altitude and the base altitude
        altitude = altitude - self.base_altitude

        data = {"latitude": latitude, "longitude": longitude,
                "gps_altitude": gps_alt, "gps_time": utc_time, "gps_quality": gps_quality, "gps_sat_num": gps_sat_num,
                "altitude": altitude, "bar_pressure": bar_pressure, "bar_temp": bar_temp,
                "gyro_x": 0, "gyro_y": 0, "gyro_z": 0,
                "acl_x": 0, "acl_y": 0, "acl_z": 0, "mag_x": 0, "mag_y": 0, "mag_z": 0}

        return data

    @staticmethod
    def get_data_header_list():

        columns = ['time', 'gps_time', 'state', 'altitude', 'gps_altitude', 'data_pulls', 'bar_pressure',
                   'bar_temp', 'gyro_x', 'gyro_y', 'gyro_z', 'acl_x', 'acl_y', 'acl_z', 'mag_x', 'mag_y', 'mag_z',
                   'latitude', 'longitude', 'gps_quality', 'gps_sat_num',
                   'cputemp']
        return columns
