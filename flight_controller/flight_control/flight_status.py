class Stage:
    pre_flight = 1
    liftoff = 2
    in_flight = 3
    apogee = 4
    descent = 5
    post_flight = 6

    def __init__(self, num):
        self.num = num


class FlightStatus:

    def __init__(self):
        self.stage = Stage(Stage.pre_flight)
        self.altitude = 0  # IDK what this should start as
        self.other_telemetry_stuff = "lorem ipsum"

    def next_stage(self):
        self.stage.num += 1


flight_status = FlightStatus()
print(flight_status.stage.num)