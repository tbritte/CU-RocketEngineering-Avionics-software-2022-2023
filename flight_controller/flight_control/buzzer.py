"""
CHANGE TICK SYSTEM FOR TIME.TIME SYSTEM
"""

import RPi.GPIO as GPIO
import time

BUZZPIN = 27


class Beep:
    """
    Has a start and a stop time, used to populate the beep_list for the buzzer
    """

    def __init__(self, start_time, stop_time):
        self.stop_time = stop_time
        self.start_time = start_time

    def should_beep(self):
        """
        Checks if the current time is between the start and stop time
        :return: True if the current time is between, false otherwise
        """
        return self.start_time < time.time() < self.stop_time

    def out_dated(self):
        """
        Checks if a beep's stop time is greater than the current time meaning that this beep
        is outdated and no longer needs to be kept track of.
        """
        return time.time() > self.stop_time


class Buzzer:
    def __init__(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(BUZZPIN, GPIO.OUT)
        self.buzzing = False
        self.beep_list = []

    def _add_beep(self, delay_from_previous_beep, duration_of_beep):
        """
        Will add another beep to the beep queue
        :param duration_of_beep: How long this beep will last
        :param delay_from_previous_beep: How long after the previous beep should be waited before this new beep
        is started. If there are no beeps already queued, then the beep will start immediately
        """
        if len(self.beep_list) > 0:  # Checking if there is another beep in the queue
            start_time = self.beep_list[-1].end_time + delay_from_previous_beep
        else:
            start_time = time.time()  # Can start immediately if not waiting for other beeps

        end_time = start_time + duration_of_beep
        self.beep_list.append(Beep(start_time, end_time))

    def _turn_on(self):
        """
        Turns the buzzer on, does nothing if it is already on.
        """
        if not self.buzzing:
            self.buzzing = True
            GPIO.output(BUZZPIN, GPIO.HIGH)

    def _turn_off(self):
        """
        Turns the buzzer off, does nothing if it is already off
        """
        if self.buzzing:
            self.buzzing = False
            GPIO.output(BUZZPIN, GPIO.LOW)

    def clear_beep_queue(self):
        """
        Clears all the beeps set to beep. Can be used to make sure a very important beep is sent out immediately
        """
        self.beep_list = []

    def update(self):
        """
        Uses the oldest beep in the queue until it becomes out of date
        Should be called every cycle within the main loop
        """
        beep = self.beep_list[0]  # Collecting the beep at the front the queue
        if beep.should_beep():
            # Starts buzzing if between this beep's beeping window
            self._turn_on()
        else:
            # Stops buzzing if outside this beep's window
            self._turn_off()

        if beep.out_dated():
            self.beep_list.pop(0)  # Removes the outdated beep

    def start_up_buzz(self):
        """
        Beeps three times rapidly to indicate that the PI has power
        """
        for _ in range(3):
            self._add_beep(delay_from_previous_beep=.25, duration_of_beep=.25)
