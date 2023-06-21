import time

from .sensors import bmp180
from .sensors import gps
from .sensors import sox
from .sensors import bno08x

from multiprocessing import Process, Queue

class ModDataHandler:
    def __init__(self):
        self.bmp180 = bmp180.BMP180()
        self.bmp180.start()

        self.gps = gps.GPS()
        self.gps.start()

        self.sox = sox.SOX()
        self.sox.start()

        # self.bno = bno08x.BNO08X()
        # self.bno.start()

    def get_data(self):
        try:
            start_time = time.monotonic()
            bmp_data = self.bmp180.get_data()
            # print("Time to get bmp data: ", time.monotonic() - start_time)

            start_time = time.monotonic()
            gps_data = self.gps.get_data()
            # print("Time to get gps data: ", time.monotonic() - start_time)

            start_time = time.monotonic()
            sox_data = self.sox.get_data()
            # print("Time to get sox data: ", time.monotonic() - start_time)

            if bmp_data is None:
                print("\n\nBMP DATA IS NONE\n\n")
                bmp_data = [0, 0, 0]
            if gps_data is None:
                gps_data = [0, 0, 0, 0, 0, 0]
            if sox_data is None:
                print("sox_data is None")
                sox_data = [0, 0, 0, 0, 0, 0, 0, 0, 0]

            print("sox_data: ", sox_data)

            altitude = bmp_data[0]
            bar_pressure = bmp_data[1]
            bar_temp = bmp_data[2]

            # [longitude, latitude, alt, quality, sat_num, utc_time]
            longitude = gps_data[0]
            latitude = gps_data[1]
            gps_alt = gps_data[2]
            gps_quality = gps_data[3]
            gps_sat_num = gps_data[4]
            utc_time = gps_data[5]


            gyro_x = sox_data[0]
            gyro_y = sox_data[1]
            gyro_z = sox_data[2]

            acl_x = sox_data[3]
            acl_y = sox_data[4]
            acl_z = sox_data[5]

            mag_x = sox_data[6]
            mag_y = sox_data[7]
            mag_z = sox_data[8]
        except Exception as e:
            print("Exception in get_data(): " + str(e))
            return None

        data = {"latitude": latitude, "longitude": longitude,
                "gps_altitude": gps_alt, "gps_time": utc_time, "gps_quality": gps_quality, "gps_sat_num": gps_sat_num,
                "altitude": altitude, "bar_pressure": bar_pressure, "bar_temp": bar_temp,
                "gyro_x": gyro_x, "gyro_y": gyro_y, "gyro_z": gyro_z,
                "acl_x": acl_x, "acl_y": acl_y, "acl_z": acl_z, "mag_x": mag_x, "mag_y": mag_y, "mag_z": mag_z}
        # print("Data being returned: " + str(data))
        print("Time to get data: " + str(time.monotonic() - start_time))
        return data

    @staticmethod
    def get_data_header_list():
        columns = ['time', 'gps_time', 'state', 'altitude', 'gps_altitude', 'data_pulls', 'bar_pressure',
                   'bar_temp', 'gyro_x', 'gyro_y', 'gyro_z', 'acl_x', 'acl_y', 'acl_z', 'mag_x', 'mag_y', 'mag_z',
                   'latitude', 'longitude', 'gps_quality', 'gps_sat_num',
                   'cputemp']
        return columns
