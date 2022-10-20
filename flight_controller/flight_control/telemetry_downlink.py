import threading
import serial


class TelemetryDownlink():
    def __init__(self, thread_name, thread_ID) -> None:
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.ser = serial.Serial("/dev/ttyUSB0", baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)
    
    def run(self):
        print(str(self.thread_name) +" "+ str(self.thread_ID))
    
    def send_data(self, data):
        print(data)
        
        data = '01101001'
        self.ser.write(data)
    
    def close(self):
        self.ser.close()