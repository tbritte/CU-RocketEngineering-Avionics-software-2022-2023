import statistics as stat
import math
from sense_emu import SenseHat


class LEDController:
    def __init__(self, sense, flight_status):
        """
        Get sense from telemetry handler because that is what initializes it
        """
        self.flight_status = flight_status
        self.sense = sense
        self.tick = 0   # To control blinking

    def fill_row(self, row, n, color):
        for i in range(n+1):
            self.sense.set_pixel(i, row, color)

    def update_lights(self):
        try:
            self.tick += 1
            self.sense.clear()
            # Getting the feet in altitude
            alt_ft = stat.median(self.flight_status.altitude_list) * 3.28
            stage_num = self.flight_status.stage.value
            self.fill_row(0, stage_num - 1, [0, 0, 255])
            self.fill_row(1, min(math.floor(alt_ft * 7 / 10000), 7), [255, 0, 0])


            # Blinking green status light
            if self.tick < 10:
                self.sense.set_pixel(7, 7, [0, 255, 0])
            elif self.tick > 20:
                self.tick = 0
        except:
            print("Light update fail")
            


