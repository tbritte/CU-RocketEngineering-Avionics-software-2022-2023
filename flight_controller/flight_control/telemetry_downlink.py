import sys
import multiprocessing
import serial
import struct
import time


def find_sync_bytes(buffer):
    """
    Find the second to last 'CRE' in the buffer. Does not use the newest 'CRE' because it may be incomplete
    :param buffer: List of bytes from the serial port read buffer
    :return: The index of the second to last 'CRE' in the buffer or -1 if no 'CRE' was found
    """

    found_newest_cre = False
    for j in range(len(buffer)):
        i = len(buffer) - j - 1  # Going backwards through the buffer
        if i < len(buffer) - 3:
            if buffer[i] == 67 and buffer[i + 1] == 82 and buffer[i + 2] == 69:  # 'C', 'R', 'E'
                if found_newest_cre:  # If we have already found the newest 'CRE'
                    return i  # Return the index of the second to last 'CRE'
                else:  # This is the newest 'CRE'
                    found_newest_cre = True
    return -1  # If we didn't find any 'CRE's


class TelemetryDownlink():
    def __init__(self) -> None:
        try:
            self.ser = serial.Serial("/dev/ttyUSB0", baudrate=57600, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)

            self.frame_count_1 = 0
            self.frame_count_2 = 0
            self.time_temp = 120000000
            self.last_gps_time_sent = 0
            self.gps_time_count_in_second = 0  # The number of GPS times sent in the last second so far
        except serial.serialutil.SerialException:
            print("No USB plugged in, telemetry downlink disabled")
            self.ser = None

        self.read_buffer = []

    # def encode_int(self, arr, num, n_bytes):
    #     arr.extend(num.to_bytes(n_bytes, byteorder='big'))

    # def encode_float(self, arr, f):
    #     arr.extend(bytearray(struct.pack("f", f)))

    def read_data(self):
        # Moving data into the buffer
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
        if self.ser is None:
            return None

        # Reading all the data on this serial port and adding it to the buffer one character at a time
        if self.ser.in_waiting > 0:
            message = str(self.ser.read(self.ser.in_waiting).decode("ascii"))
            print("\n\n\nMessage:\n\n\n ", message)
        else:
            return None
        # self.read_buffer.append(self.ser.read(self.ser.in_waiting))

        # # Trimming the beginning of the buffer to remove any old data
        # if len(self.read_buffer) > 100:
        #     self.read_buffer = self.read_buffer[-100:]
        # print(self.read_buffer)
        # # Searching for the most recent complete message by finding the second to last 'CRE'
        # index_second_to_last_cre = find_sync_bytes(self.read_buffer)
        # if index_second_to_last_cre == -1:
        #     print("No complete message found")
        #     return None
        #
        # # Getting the data from the second to last 'CRE'
        # byte_message = self.read_buffer[index_second_to_last_cre:index_second_to_last_cre + 11]
        #
        # # Converting the first 7 bytes to a string and calculating the checksum
        # message = ""
        # checksum = 0
        # for i in range(7):
        #     message += byte_message[i].decode('ascii')
        #     checksum ^= byte_message[i]
        #
        # print("Checksum= " + str(checksum) + "Final decoded message: " + message)

        # Decoding the message to see which camera to turn on
        if message[3:6] == 'CAM':  # We are turning on a camera
            return int(message[6])  # returning the camera number
        elif message[3:6] == 'RDY':
            print("----Received ready message----")
        else:
            print("Unknown message, I don't know what to do with it...")

        # QZMP for DSRM

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
        # print("Status bits: ", status_bits)
        for i in range(16):
            stat_num ^= status_bits[stats[i]] * (2 ** i)

        # print(stat_num, bin(stat_num))

        # Adding 1/8s to the GPS time if it is the same as the last GPS time sent until a new second is reached
        current_gps_time = float(data['gps_time'])
        if current_gps_time == self.last_gps_time_sent:
            self.gps_time_count_in_second += 1
            current_gps_time += self.gps_time_count_in_second * .125
        else:
            self.gps_time_count_in_second = 0

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
        data_arr.extend(bytearray(struct.pack("L", int(current_gps_time * 1000))))
        data_arr.extend(bytearray(struct.pack("H", 0)))  # Heading
        data_arr.extend(bytearray(struct.pack("H", stat_num)))  # Status

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
        # print("\n", checksum, "Sent data:", data)
        # Sending the written data
        # self.ser.flush()
        # ser.flush is used to clear the buffer and send the data immediately without waiting for the buffer to fill up

    def close(self):
        self.ser.close()
        pass
