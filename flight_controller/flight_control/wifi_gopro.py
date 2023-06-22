from threading import Thread
import time

ids = [{"ssid": "gopro1", "password": "fart"},
       {"ssid": "gopro2", "password": "face"},
       {"ssid": "gopro3", "password": "butt"}]


class WifiGoProSystem(Thread):
    """
    Create an instance of this class to start the Wi-Fi gopro system
    """
    def __init__(self):
        super().__init__()
        self.activation_queue = []

        self.start()  # Starts itself

    def activate_gopro(self, num):
        """
        Adds the given gopro number to the activation queue.
        This is the function that should be called within the flight_controller
        """
        self.activation_queue.append(num)

    def _turn_on_gopro(self, num):
        """
        Somehow connect to the gopro here and turn it on
        Should only be called in a thread so that it doesn't slow down the main thread
        Because this should be called from within `run`, it shouldn't slow down the main thread
        """
        pass

    def run(self):
        while True:
            time.sleep(.1)
            if len(self.activation_queue) > 0:
                self._turn_on_gopro(self.activation_queue.pop(0))


