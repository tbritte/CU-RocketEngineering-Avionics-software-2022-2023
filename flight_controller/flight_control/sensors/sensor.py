from threading import Thread
from multiprocessing import Process, Queue
import time


class Sensor(Process):
    def __init__(self, name):
        print("Setting up {}".format(name))
        super().__init__()  # Sets up the thread part of the object
        self.functional = False
        self.most_recent_data = None
        self.most_recent_quality_data = None
        self.queue = Queue()
        self.setup()


    def setup(self):
        raise NotImplementedError

    def get_new_data(self):
        raise NotImplementedError

    def _update_data(self):
        if self.functional:
            self.most_recent_data = self.get_new_data()
        else:
            print("({}) Trying to setup again".format(self.sensor_name))
            self.setup()

        self.queue.put(self.most_recent_data)

    def run(self):
        while True:
            self._update_data()
            time.sleep(.01)

    def get_data(self):
        # Getting the most recent of the queue
        data = None
        while not self.queue.empty():
            data = self.queue.get()

        # Sometimes data is None becasue the queue was empty, so just use the most recent data that had been used
        if data is not None:
            self.most_recent_quality_data = data

        return self.most_recent_quality_data
