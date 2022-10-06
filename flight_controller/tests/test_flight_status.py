from flight_status import FlightStatus

def test_flight_status():
    flight_status = FlightStatus()
    flight_status.new_telemetry({'altitude': 12, 'raw_accelerometer': 8})
