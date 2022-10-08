import random

from flight_control import FlightStatus

def test_current_stage():
    flightStatus = FlightStatus()
    assert flightStatus.current_stage().value == 1
    assert flightStatus.current_stage_name() == 'PRE_FLIGHT'

def test_add_altitude():
    flightStatus = FlightStatus()
    
    altitudes = [random.randint(0, 100) for i in range(64)]
    
    for altitude in altitudes:
        flightStatus.add_altitude(altitude)
    
    assert flightStatus.altitude_list == altitudes

def test_check_apogee():
    flightStatus = FlightStatus()
    for i in range(64):
        flightStatus.add_altitude(i + random.randint(-10, 10))
    passed_apogee = flightStatus.check_apogee()
    assert not passed_apogee
    
    for i in range(64):
        flightStatus.add_altitude(64 - i + random.randint(-10, 10))
    passed_apogee = flightStatus.check_apogee()
    assert passed_apogee

def test_check_apogee_extreme_noise():
    flightStatus = FlightStatus()
    for i in range(64):
        flightStatus.add_altitude(i + random.randint(-50, 50))
    passed_apogee = flightStatus.check_apogee()
    assert not passed_apogee
    
    for i in range(64):
        flightStatus.add_altitude(64 - i + random.randint(-50, 50))
    passed_apogee = flightStatus.check_apogee()
    assert passed_apogee
