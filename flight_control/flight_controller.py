from .telemetry_downlink import TelemetryDownlink
from .telemetry_handler import TelemetryHandler

def main():
    telemetryHandler = TelemetryHandler()
    telemetryDownlink = TelemetryDownlink("Telemetry Downlink", 1000)
    
    telemetryDownlink.start()
    

if __name__ == '__main__':
    main()