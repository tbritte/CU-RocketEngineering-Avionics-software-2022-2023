from subprocess import call
import time

from .parachute import Parachute

from .flight_status import FlightStatus
from .flight_status import Stage

from .telemetry_downlink import TelemetryDownlink
from .telemetry_handler import TelemetryHandler

from .data_logging import DataLogger


start_time = time.time()
telemetry_logger = DataLogger('telemetry_log.csv', ['time', 'humidity', 'pressure', 'altitude', 'humidity_temp',
                          'pressure_temp', 'temp', 'orientation', 'raw_accelerometer', 'north', 'raw_magnetometer'], start_time)
flight_status = FlightStatus()

def main():
    telemetryHandler = TelemetryHandler()
    telemetryDownlink = TelemetryDownlink("Telemetry Downlink", 1000)

    #telemetryDownlink.run()
    
    terminate = False
    
    last_data_pull = time.time()
    
    while not terminate:
        if time.time() - last_data_pull > 0.0625:
            last_data_pull = time.time()
            print(flight_status.stage.name)
            data = telemetryHandler.get_data()
            telemetry_logger.log_data(data)
            #telemetryDownlink.send_data(data)
            flight_status.new_telemetry(data) 
        if flight_status.current_stage() == Stage.DESCENT:
            parachute = Parachute()
            parachute.deploy()
        
        if flight_status.current_stage() == Stage.ON_GROUND:
            parachute.kill_signal()
            terminate = True
    
    #call(['shutdown', '-h', 'now'], shell=False)

if __name__ == '__main__':
    main()
