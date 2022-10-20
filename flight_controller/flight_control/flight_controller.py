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
    
    terminate = False
    
    last_data_pull = time.time()
    
    while not terminate:
        if last_data_pull - time.time() > 0.25:
            last_data_pull = time.time()
            
            data = telemetryHandler.get_data()
            telemetry_logger.log_data(data)
            telemetryDownlink.send_data(data)
        
        if flight_status.current_stage() == FlightStatus.flight:
            parachute = Parachute()
            parachute.deploy()
            flight_status.set_status(FlightStatus.post_flight)
            terminate = True


if __name__ == '__main__':
    main()
