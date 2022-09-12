from .telemetry_downlink import TelemetryDownlink
from .telemetry_handler import TelemetryHandler

from .logging import Logger

TELEMETRY_LOG = 'telemetry_log.csv'

def main():
    telemetryHandler = TelemetryHandler()
    telemetryDownlink = TelemetryDownlink("Telemetry Downlink", 1000)
    
    telemetryDownlink.start()
    
    telemetryHandler.print_data()
    

if __name__ == '__main__':
    main()