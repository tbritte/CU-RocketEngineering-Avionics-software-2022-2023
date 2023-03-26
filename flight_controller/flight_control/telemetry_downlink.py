import sys
import multiprocessing
import serial
import struct
import time


class TelemetryDownlink():
    def __init__(self) -> None:
        try:
            self.ser = serial.Serial("/dev/ttyUSB0", baudrate=57600, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)

            self.frame_count_1 = 0
            self.frame_count_2 = 0
            self.time_temp = 120000000
        except serial.serialutil.SerialException:
            print("No USB plugged in, telemetry downlink disabled")
            self.ser = None

    # def encode_int(self, arr, num, n_bytes):
    #     arr.extend(num.to_bytes(n_bytes, byteorder='big'))

    # def encode_float(self, arr, f):
    #     arr.extend(bytearray(struct.pack("f", f)))

    def read_data(self):
        # Reading in 11 bytes
        """
        1 - sync 0 ('C')
        1 - sync 1 ('R')
        1 - sync 2 ('E')
        1 - message char 1
        1 - message char 2
        1 - message char 3
        1 - message char 4
        4 - Checksum (xor of all other bytes)

        Returns: The message as string
        """
        print("\nReading data...")
        # Read in 11 bytes
        try:
            data = self.ser.read(11)
        except:
            print("Error reading 11 bytes")
            return

        message = ""
        if len(data) == 11:
            # Converting all the bytes except for the last one to a string of characters
            for i in range(10):
                message += data[i].decode('ascii')

            # Check if the first three characters are 'CRE'
            if message[0:3] == "CRE":  # message[0:3] is the first three characters
                # Check if the checksum is correct
                checksum = 0
                # Using all bytes except the last one
                for i in range(10):
                    checksum ^= data[i]
            else:
                print("Does not have correct sync bytes... "
                      "has " + message[0:3] + " instead")
        else:
            print("Does not have 11 bytes has " + str(len(data)) + " bytes instead")

        print("Raw decoded message: " + message)

        # Decoding the message to see which camera to turn on
        if message[3:6] == 'CAM':  # We are turning on a camera
            return int(message[6])  # returning the camera number
        elif message[3:6] == 'RDY':
            print("----Received ready message----")
        else:
            print("Unknown message, I don't know what to do with it...")

    def send_data(self, data, status_bits):
        """
        1 - sync 0
        1 - sync 1
        1 - sync 2
        2 - MFC1
        2 - MFC2
        4 - Altitude
        4 - Acceleration_Z
        4 - Acceleration_Y
        4 - Acceleration_X
        4 - Gyro_Z
        4 - Gyro_Y
        4 - Gyro_X
        4 - Magnetometer_Z
        4 - Magnetometer_Y
        4 - Magnetometer_X
        4 - Temperature
        4 - Predicted apogee
        4 - Humidity
        4 - GPS Latitude
        4 - GPS Longitude
        4 - GPS Altitude
        8 - Time of data collection
        2 - Heading
        2 - Status
        1 - Checksum
        """

        # Calculating the status number from the status bits
        stat_num = 0
        stats = ["active aero", "excessive spin", "excessive vibration", "on", "Nominal", "launch detected",
                 "apogee detected", "drogue deployed", "main deployed", "touchdown", "payload deployed", "Pi Cam 1 On",
                 "Pi Cam 2 On", "Go Pro 1 On", "Go Pro 2 On", "Go Pro 3 On"]

        for i in range(16):
            stat_num ^= status_bits[stats[i]] * 2 ** i

        print(stat_num, bin(stat_num))

        data_arr = bytearray()

        # Append sync bytes to data arr
        data_arr.extend(bytes('CRE', 'ascii'))
        data_arr.extend(bytearray(struct.pack("H", self.frame_count_1)))
        data_arr.extend(bytearray(struct.pack("H", self.frame_count_2)))
        data_arr.extend(bytearray(struct.pack("f", data['altitude'])))
        data_arr.extend(bytearray(struct.pack("f", data['acl_x'])))
        data_arr.extend(bytearray(struct.pack("f", data['acl_y'])))
        data_arr.extend(bytearray(struct.pack("f", data['acl_z'])))
        data_arr.extend(bytearray(struct.pack("f", data['gyro_x'])))
        data_arr.extend(bytearray(struct.pack("f", data['gyro_y'])))
        data_arr.extend(bytearray(struct.pack("f", data['gyro_z'])))
        data_arr.extend(bytearray(struct.pack("f", data['mag_x'])))
        data_arr.extend(bytearray(struct.pack("f", data['mag_y'])))
        data_arr.extend(bytearray(struct.pack("f", data['mag_z'])))
        data_arr.extend(bytearray(struct.pack("f", data['bar_temp'])))
        data_arr.extend(bytearray(struct.pack("f", data['predicted_apogee'])))
        data_arr.extend(bytearray(struct.pack("f", 0)))  # Humidity no sensor for it
        data_arr.extend(bytearray(struct.pack("f", data['latitude'])))
        data_arr.extend(bytearray(struct.pack("f", data['longitude'])))
        data_arr.extend(bytearray(struct.pack("f", data['gps_altitude'])))
        data_arr.extend(bytearray(struct.pack("L", int(time.time()))))
        data_arr.extend(bytearray(struct.pack("H", 0)))  # Heading
        data_arr.extend(bytearray(struct.pack("H", 0)))  # Status

        self.time_temp += 125

        # for i, d in enumerate(data_arr):
        #     print("index:", i, d)

        # Calculate checksum
        checksum = 0
        for byte in data_arr:
            checksum ^= byte
        # print("checksum: " + str(checksum))
        data_arr.extend(bytearray(struct.pack("B", checksum)))
        # print("checksumbutearray: ", bytearray(struct.pack("B", checksum)))

        self.frame_count_1 += 1
        if self.frame_count_1 >= 2 ** 15 - 1:
            self.frame_count_1 = 0
            self.frame_count_2 += 1

        # print(data_arr)
        self.ser.write(data_arr)
        # self.ser.write(bytes('CRE', 'ascii'))
        print("\n", checksum, "Sent data:", data)
        # Sending the written data
        # self.ser.flush()
        # ser.flush is used to clear the buffer and send the data immediately without waiting for the buffer to fill up

    def close(self):
        self.ser.close()
        pass
