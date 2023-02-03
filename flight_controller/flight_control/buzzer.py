"""
CHANGE TICK SYSTEM FOR TIME.TIME SYSTEM
"""

import RPi.GPIO as GPIO

BUZZPIN = 27


class Buzzer:
    def __init__(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(BUZZPIN, GPIO.OUT)
        self.buzzing = False
        self.doing_three_second_buzz = False
        self.doing_half_cycle_buzz = False
        self.tick = 0

    def turn_on(self):
        """Turns the buzzer on, does nothing if it is already on.
        """
        if not self.buzzing:
            self.buzzing = True
            GPIO.output(BUZZPIN, GPIO.HIGH)

    def turn_off(self):
        """
        Turns the buzzer off, does nothing if it is already off
        """
        if self.buzzing:
            self.buzzing = False
            GPIO.output(BUZZPIN, GPIO.LOW)

    def update(self):
        """ Updates the tick counter for timed buzzing call it every rocket calculation cycle"""
        if self.doing_three_second_buzz:
            self.tick += 1
            if self.tick > 48:
                self.doing_three_second_buzz = False
                self.turn_off()
        elif self.doing_half_cycle_buzz:
            self.tick += 1
            self.tick %= 32  # 32 ticks is equal to 2 seconds
            if self.tick < 16:  # Buzzes for the first second
                self.turn_on()
            else:  # Does not buzz for the second second
                self.turn_off()

    def trigger_three_second_buzz(self):
        """
        Begins a three-second buzz by turning on the buzzer and starting a timer
        If the three-second buzz has already been started this has no effect
        """
        if not self.doing_three_second_buzz:
            self.tick = 0
            self.doing_three_second_buzz = True
            self.turn_on()

    def trigger_half_cycle(self):
        """
        Starts a cycle of one second buzz with one second no buzz
        Cancels a three-second buzz if that has started
        Has no effect if the half cycle buzz has already been started
        """
        if not self.doing_half_cycle_buzz:
            self.doing_half_cycle_buzz = True
            self.doing_three_second_buzz = False  # Cancels the three-second buzz
            self.tick = 0



