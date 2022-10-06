import pandas as pd

from flight_control import TelemetryHandler

def test_telemetry_handler():
    telemetryHandler = TelemetryHandler()
    telemetryHandler.print_data()
