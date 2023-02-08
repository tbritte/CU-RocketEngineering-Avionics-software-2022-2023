import statistics as stat
import math
from sense_hat import SenseHat

ALL_WHITE = [[255, 255, 255] for _ in range(64)]


class LEDController:
    def __init__(self, sense, flight_status, camera):
        """
        Get sense from telemetry handler because that is what initializes it
        """
        self.flight_status = flight_status
        self.sense = sense
        self.camera = camera
        self.has_been_armed = False
        self.showing_arm_tick = 0
        self.tick = 0  # To control blinking

    def fill_row(self, row, n, color):
        for i in range(n + 1):
            self.sense.set_pixel(i, row, color)

    def update_lights(self):
        try:
            self.tick += 1
            self.sense.clear()
            # Getting the feet in altitude
            alt_ft = stat.median(self.flight_status.altitude_list) * 3.28
            stage_num = self.flight_status.stage.value
            self.fill_row(0, stage_num - 1, [0, 0, 255])
            self.fill_row(1, min(math.floor(alt_ft / 10), 7), [255, 0, 0])

            # Blinking green status light
            if self.tick < 10:
                self.sense.set_pixel(7, 7, [0, 255, 0])
                if self.camera.recording:
                    self.sense.set_pixel(6, 7, [255, 0, 0])
            elif self.tick > 20:
                self.tick = 0

            # Detects when the rocket has been armed and triggers 50 cycles of bright white
            if self.flight_status.stage.value == 1 and not self.has_been_armed:
                self.has_been_armed = True
                self.showing_arm_tick = 50

            if self.showing_arm_tick > 0:
                self.showing_arm_tick -= 1
                self.sense.set_pixels(ALL_WHITE)
        except:
            print("Light update fail")
