import time

from .parachute import Parachute

from .flight_status import FlightStatus

from .telemetry_downlink import TelemetryDownlink
from .telemetry_handler import TelemetryHandler

from .data_logging import DataLogger


start_time = time.time()
telemetry_logger = DataLogger('telemetry_log.csv', ['time', 'humidity', 'pressure', 'altitude', 'humidity_temp',
                          'pressure_temp', 'temp', 'orientation', 'raw_accelerometer', 'north', 'raw_magnetometer'], start_time)
flight_status = FlightStatus.pre_flight

def main():
    telemetryHandler = TelemetryHandler()
    telemetryDownlink = TelemetryDownlink("Telemetry Downlink", 1000)

    telemetryDownlink.start()
    
    telemetryHandler.print_data()


if __name__ == '__main__':
    main()
