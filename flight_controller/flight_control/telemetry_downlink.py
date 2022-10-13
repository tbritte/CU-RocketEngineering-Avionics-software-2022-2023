import threading

class TelemetryDownlink():
    def __init__(self, thread_name, thread_ID) -> None:
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
    
    def run(self):
        print(str(self.thread_name) +" "+ str(self.thread_ID))