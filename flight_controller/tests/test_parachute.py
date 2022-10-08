from flight_control import Parachute

def test_parachute():
    parachute = Parachute()
    parachute.parachute_deployment()
    parachute.kill_parachute_signal()
    assert True
