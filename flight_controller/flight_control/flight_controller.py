import time

from .telemetry_downlink import TelemetryDownlink
from .telemetry_handler import TelemetryHandler

from .logging import Logger


start_time = time.time()
telemetry_logger = Logger('telemetry_log.csv', ['time', 'humidity', 'pressure', 'humidity_temp',
                          'pressure_temp', 'temp', 'orientation', 'raw_accelerometer', 'north', 'raw_magnetometer'], start_time)


def main():
    telemetryHandler = TelemetryHandler()
    telemetryDownlink = TelemetryDownlink("Telemetry Downlink", 1000)

    telemetryDownlink.start()

    telemetryHandler.print_data()


if __name__ == '__main__':
    main()
