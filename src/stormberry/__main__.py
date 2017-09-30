from stormberry import Config
import logging
import signal
import sys
from stormberry import WeatherStation

class SignalHandling(object):
    """
    Does graceful signal handling for heartbeat.
    """
    def __init__(self, station):
        self.station = station

    def __enter__(self):
        signal.signal(signal.SIGQUIT, self.station.stop_station)
        signal.signal(signal.SIGTERM, self.station.stop_station)
        signal.signal(signal.SIGINT, self.station.stop_station)

    def __exit__(self, type, value, traceback):
        # Ideally this would restore the original
        # signal handlers, but that isn't functionality
        # that's needed right now, so we'll do nothing.
        pass

def main():

    config = Config()
    # Setup logger, to log warning/errors during execution
    logging.basicConfig(
            filename=config.get("GENERAL", "LOGFILE"),
            format='\r\n%(asctime)s %(levelname)s %(message)s', 
            level=logging.WARNING
            )

    # Make sure we don't have an upload interval more than 3600 seconds
    if config.getint("GENERAL", "UPLOAD_INTERVAL") > 3600:
        print('The application\'s upload interval cannot be greater than 3600 seconds')
        logging.warning('The application\'s upload interval cannot be greater than 3600 seconds')

        sys.exit(1)

    try:
        station = WeatherStation(config)

        station.activate_sensors()
        print('Successfully initialized sensors')

        data = station.get_sensors_data()
        print(station.READINGS_PRINT_TEMPLATE % data.tuple)
        with SignalHandling(station) as sh:
            station.start_station()
            print('Weather Station successfully launched')

    except:
        station.stop_station()

        sys.exit(0)
