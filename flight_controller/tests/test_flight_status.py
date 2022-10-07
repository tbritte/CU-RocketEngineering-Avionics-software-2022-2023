import logging
import random

from flight_control import FlightStatus

def test_current_stage():
    flightStatus = FlightStatus()
    assert flightStatus.current_stage().value == 1
    assert flightStatus.current_stage_name() == 'PRE_FLIGHT'

def test_add_altitude():
    flightStatus = FlightStatus()
    for i in range(20):
        flightStatus.add_altitude(random.randint(0,10000))
        
    logging.info(flightStatus.altitude_list)

def test_check_apogee():
    flightStatus = FlightStatus()
    for i in range(64):
        flightStatus.add_altitude(i + random.randint(-10, 10))
    flightStatus.check_apogee()