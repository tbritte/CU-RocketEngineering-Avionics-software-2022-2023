import sys
import multiprocessing
import serial
import struct


class TelemetryDownlink():
    def __init__(self, thread_name, thread_ID) -> None:
        self.ser = serial.Serial("/dev/ttyUSB1", baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)
        
        self.frame_count_1 = 0
        self.frame_count_2 = 0
    
    def run(self):
        print(str(self.thread_name) +" "+ str(self.thread_ID))
        try:
            self.ser.open()
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(self.ser.name, e))
            exit()
    
    # def encode_int(self, arr, num, n_bytes):
    #     arr.extend(num.to_bytes(n_bytes, byteorder='big'))
    
    # def encode_float(self, arr, f):
    #     arr.extend(bytearray(struct.pack("f", f)))
    
    def send_data(self, data):
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
        print(data)
        
        data = '01101001'
        
        data_arr = bytearray()
        
        # Append sync bytes to data arr
        data_arr.extend(bytes('CRE', 'ascii'))
        data_arr.extend(bytearray(struct.pack("H", frame_count_1)))
        data_arr.extend(bytearray(struct.pack("H", frame_count_2)))
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
        data_arr.extend(bytearray(struct.pack("f", data['temp'])))
        data_arr.extend(bytearray(struct.pack("f", data['predicted_apogee'])))
        data_arr.extend(bytearray(struct.pack("f", data['humidity'])))
        data_arr.extend(bytearray(struct.pack("f", data['latitude'])))
        data_arr.extend(bytearray(struct.pack("f", data['longitude'])))
        data_arr.extend(bytearray(struct.pack("f", data['gps_altitude'])))
        data_arr.extend(bytearray(struct.pack("d", data['gps_time'])))
        data_arr.extend(bytearray(struct.pack("H", data['heading'])))
        data_arr.extend(bytearray(struct.pack("H", data['status'])))
        
        # Calculate checksum
        for byte in data_arr:
            checksum ^= byte
        data_arr.extend(bytearray(struct.pack("B", checksum)))
        
        frame_count_1 += 1
        if frame_count_1 >= 1023:
            frame_count_1 = 0
            frame_count_2 += 1
        
        self.ser.write(data_arr)
    
    def close(self):
        self.ser.close()
        pass
