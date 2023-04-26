from threading import Thread
import time


class Sensor(Thread):
    def __init__(self, name):
        print("Setting up {}".format(name))
        super().__init__()  # Sets up the thread part of the object
        self.functional = False
        self.most_recent_data = None
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

    def get_data(self):
        return self.most_recent_data

    def run(self):
        time_from_last_update = time.monotonic()
        while True:
            if (time.monotonic() - time_from_last_update) > .01:
                self._update_data()
                time_from_last_update = time.monotonic()
            time.sleep(.01)
