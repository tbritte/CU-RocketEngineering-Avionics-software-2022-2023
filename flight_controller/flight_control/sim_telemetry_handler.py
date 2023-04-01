import time
import pandas as pd
import numpy as np
import sys
sys.path.append("simulation") # Putting the simulation folder in the path


# Should be in the simulation folder
DATA_NAME = "simulation/testdata.csv"

class SimTelemetryHandler:
    def __init__(self):
        self.start_time = time.time()

        # Loading in testdata using pandas and then storing it as a numpy array
        self.data = pd.read_csv(DATA_NAME)
        print("ALL DATA IS HERE:", self.data)
        self.data = self.data.to_numpy()

    def setup(self):
        pass

    def get_data(self):

        # Getting elapsed time to query the csv data with
        elapsed_time = time.time() - self.start_time + 340  # To get to the exciting part of the flight

        # Using the time column to find the closest time to the elapsed time and then using that index to get the data
        index = np.abs(self.data[:,0] - elapsed_time).argmin()

        # Using the index to get data
        altitude = self.data[index, 1]

        # Average of the three axis, only one axis is significant, so the avg doesn't have a difference from vertical
        acl_avg = self.data[index, 2]

        # print("USEFUL DATA FROM SIMULATION: ", elapsed_time, altitude, acl_avg)

        # Most value are zero
        data = {"latitude": 1345, "longitude": 7832,
                "gps_altitude": 0, "gps_time": 0, "gps_quality": 0, "gps_sat_num": 0,
                "altitude": altitude, "bar_pressure": 7, "bar_temp": 69,
                "gyro_x": 420, "gyro_y": 69, "gyro_z": 420,
                "acl_x": acl_avg, "acl_y": 32, "acl_z": 16, "mag_x": 8, "mag_y": 4, "mag_z": 2}
        return data

    @staticmethod
    def get_data_header_list():
        columns = ['time', 'gps_time', 'state', 'altitude', 'gps_altitude', 'data_pulls', 'bar_pressure',
                   'bar_temp', 'gyro_x', 'gyro_y', 'gyro_z', 'acl_x', 'acl_y', 'acl_z', 'mag_x', 'mag_y', 'mag_z',
                   'latitude', 'longitude', 'gps_quality', 'gps_sat_num',
                   'cputemp']
        return columns
