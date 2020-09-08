from stormberry.config import Config
import signal
import sys
import stormberry.logging
from stormberry.station import WeatherStation
from stormberry.plugin import ISensorPlugin, IRepositoryPlugin, IDisplayPlugin, PluginDataManager
from stormberry.plugin.manager import get_plugin_manager


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

    try:
        logdir = config.get("GENERAL", "LOGDIR")
    except:
        logdir = "/tmp"

    filehandler, termhandler = stormberry.logging.setup_handlers(logdir, "stormberry-station.log")
    stormberry_logger = stormberry.logging.setup_logging(config, "stormberry-station", [filehandler, termhandler])
    yapsy_logger = stormberry.logging.setup_logging(config, "yapsy", [filehandler, termhandler])

    plugin_manager = get_plugin_manager(config)

    plugins = plugin_manager.getAllPlugins()
    plugin_names = str([x.plugin_object.__class__.__name__ for x in plugins])
    stormberry_logger.info("Loaded %d plugins: %s" % (len(plugins), plugin_names))

    plugin_data_manager = PluginDataManager()
    try:
        station = WeatherStation(plugin_manager, config, plugin_data_manager, stormberry_logger)

        station.prepare_sensors()
        station.prepare_repositories()
        station.prepare_displays()

        stormberry_logger.info('Successfully initialized sensors')

        with SignalHandling(station) as sh:
            station.start_station()
            stormberry_logger.info('Weather Station successfully launched')
            signal.pause()

    except Exception as e:
        stormberry_logger.critical(e)
        station.stop_station()

        sys.exit(0)
