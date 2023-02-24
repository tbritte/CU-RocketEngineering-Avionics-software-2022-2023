import sys
import threading
import serial


class TelemetryDownlink(threading.Thread):
    def __init__(self, thread_name, thread_ID) -> None:
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
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
    
    def send_data(self, data):
        """
        1 - 'C'
        1 - 'R'
        1 - 'E'
        1 - '1' or '2' - system which talk to
        2 - FRAME COUNT
        2 - FRAME COUNT2
        4 - Altitude
        4 - AcclZ
        4 - AcclY
        4 - AcclX
        4 - GyroZ
        4 - GyroY
        4 - GyroX
        4 - Magnetometer_Z
        4 - Magnetometer_Y
        4 - Magnetometer_X
        4 - Temp
        4 - P_Apogee
        4 - Humidity
        4 - GPS LAT
        4 - GPS LONG
        4 - GPS Altitude
        4 - Time
        2 - Stage
        1 - Checksum
        """
        print(data)
        
        data = '01101001'
        
        data_arr = bytearray()
        
        # Append sync bytes to data arr
        data_arr.append(bytes('CRE', 'utf-8'))
        data_arr.append(bytes(1))
        data_arr.append(bytes(frame_count_1))
        data_arr.append(bytes(frame_count_2))
        data_arr.append(bytes(data['altitude']))
        data_arr.append(bytes(data['raw_accelerometer']['z']))
        data_arr.append(bytes(data['raw_accelerometer']['y']))
        data_arr.append(bytes(data['raw_accelerometer']['x']))
        data_arr.append(bytes(data['raw_gyroscope']['z']))
        
        
        frame_count_1 += 1
        if frame_count_1 >= 1023:
            frame_count_1 = 0
            frame_count_2 += 1
        
        byte_message = bytes('Hello World', 'utf-8')
        self.ser.write(byte_message)
    
    def close(self):
        self.ser.close()
        pass
