from flight_control import FlightStatus

def test_current_stage():
    flightStatus = FlightStatus()
    assert flightStatus.current_stage() == 1
    assert flightStatus.current_stage_name() == 'pre_flight'
