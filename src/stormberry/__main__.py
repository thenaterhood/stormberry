from stormberry import Config
import logging, logging.handlers
import signal
import sys
from stormberry import WeatherStation
from yapsy.PluginManager import PluginManager

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
    plugin_manager = PluginManager()
    logger = logging.getLogger('stormberry')
    logger.setLevel(logging.DEBUG)

    try:
        filehandler = logging.handlers.TimedRotatingFileHandler(
                filename=config.get("GENERAL", "LOGFILE"),
                when="W0"
                )
    except:
        filehandler = logging.handlers.TimedRotatingFileHandler(
                filename="/tmp/stormberry.log",
                when="W0"
                )

    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(name)s;%(message)s",
            "%Y-%m-%d %H:%M:%S")
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

    termhandler = logging.StreamHandler(sys.stdout)
    termhandler.setLevel(logging.INFO)
    logger.addHandler(termhandler)

    plugin_manager.setPluginPlaces(
            [config.get("GENERAL", "PLUGIN_DIRECTORY")]
            )
    plugin_manager.collectPlugins()
    plugins = plugin_manager.getAllPlugins()
    logger.info("Loaded %d plugins" % len(plugins))

    # Make sure we don't have an upload interval more than 3600 seconds
    if config.getint("GENERAL", "UPLOAD_INTERVAL") > 3600:
        logger.error('The application\'s upload interval cannot be greater than 3600 seconds')

        sys.exit(1)

    try:
        station = WeatherStation(plugin_manager, config, logger)

        station.activate_sensors()
        logger.info('Successfully initialized sensors')

        data = station.get_sensors_data()
        logger.info("Initial Reading: " + station.READINGS_PRINT_TEMPLATE % data.tuple)
        with SignalHandling(station) as sh:
            station.start_station()
            logger.info('Weather Station successfully launched')
            signal.pause()

    except Exception as e:
        logger.critical(e)
        station.stop_station()

        sys.exit(0)
