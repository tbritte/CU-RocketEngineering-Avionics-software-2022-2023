import logging
import random

from flight_control import FlightStatus

def test_current_stage():
    flightStatus = FlightStatus()
    assert flightStatus.current_stage() == 1
    assert flightStatus.current_stage_name() == 'pre_flight'

def test_add_altitude():
    flightStatus = FlightStatus()
    for i in range(20):
        flightStatus.add_altitude(random.randint(0,10000))
        
    logging.info(flightStatus.altitude_list)
