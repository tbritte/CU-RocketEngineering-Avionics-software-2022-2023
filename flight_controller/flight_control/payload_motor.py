from TMC_2209.TMC_2209_StepperDriver import *
import time

en, step, dir = 21, 16, 20

"""
en enables the motor output
step moves the motor one step per pulse
dir sets the direction of the motor
"""

class Payload:
    def __init__(self):
        """
        Configuring the TMC_2209 stepper driver
        """
        self.tmc = TMC_2209(en, step, dir)
        self.tmc.set_direction_reg(False)
        self.tmc.set_current(300)
        self.tmc.set_interpolation(True)
        self.tmc.set_spreadcycle(False)
        self.tmc.set_microstepping_resolution(2)
        self.tmc.set_internal_rsense(False)

        self.tmc.set_acceleration(2000)
        self.tmc.set_max_speed(500)

        self.tmc.set_motor_enabled(True)

        """
        Status variables
        """

        self.deployed = False
        self.deploying = False
        self.deploying_start_time = 0

    def deploy_payload(self):
        if not self.deployed and not self.deploying:
            self.deploying = True
            self.deploying_start_time = time.time()
            print("(payload motor) payload deployment started")
            self.tmc.run_to_position(400)

    def update(self):
        if self.deploying:
            if time.time() - self.deploying_start_time > 2:  # Hangs open for about this many seconds
                self.tmc.run_to_position(0)
                self.deployed = True
                self.deploying = False
                print("(payload motor) payload deployment finished")

