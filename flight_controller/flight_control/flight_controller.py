from subprocess import call
import time

from .parachute import Parachute

from .flight_status import FlightStatus
from .flight_status import Stage

from .telemetry_downlink import TelemetryDownlink
from .telemetry_handler import TelemetryHandler

from .data_logging import DataLogger

from .camera import Camera
from .LED_controller import LEDController

start_time = time.time()
telemetry_logger = DataLogger('telemetry_log.csv', ['time', 'humidity', 'pressure', 'altitude', 'humidity_temp',
                          'pressure_temp', 'temp', 'orientation', 'raw_accelerometer', 'north', 'raw_magnetometer'], start_time)

def startup(telemetryHandler: TelemetryHandler, telemetryDownlink: TelemetryDownlink):
    telemetryHandler.setup()
    telemetryDownlink.run()

def main():
    telemetry_handler = TelemetryHandler()
    # telemetry_downlink = TelemetryDownlink("Telemetry Downlink", 1000)
    
    # startup(telemetryHandler=telemetry_handler, telemetryDownlink=telemetry_downlink)
    telemetry_handler.setup()
    
    flight_status = FlightStatus(telemetry_handler.sense)
    parachute = Parachute()
    
    camera = Camera("/home/curocket/Rocket/")
    led_controller = LEDController(telemetry_handler.sense, flight_status, camera)
    
    terminate = False
    
    last_data_pull = time.time()
    
    while not terminate:
        if time.time() - last_data_pull > 0.0625:
            last_data_pull = time.time()
            
            print(flight_status.stage.name)
            data = telemetry_handler.get_data()
            telemetry_logger.log_data(data)
            #telemetryDownlink.send_data(data)
            flight_status.new_telemetry(data) 
            led_controller.update_lights()
            
        if flight_status.current_stage() == Stage.PRE_FLIGHT:
            if not camera.recording:
                camera.start_recording()
        if flight_status.current_stage() == Stage.DESCENT and not parachute.deployed:
            parachute.deploy()
        elif flight_status.current_stage() == Stage.DESCENT and parachute.deployed:
            parachute.kill_signal()
        elif flight_status.current_stage() == Stage.ON_GROUND:
            if camera.recording:
                camera.stop_recording()
            terminate = True
    
    #call(['shutdown', '-h', 'now'], shell=False)

if __name__ == '__main__':
    main()
