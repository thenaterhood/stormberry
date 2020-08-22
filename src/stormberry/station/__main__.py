from stormberry.config import Config
import logging, logging.handlers
import signal
import sys
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

def set_handler_level_from_str(logger, level_name):
    try:
        logger.setLevel(level_name.upper())
    except:
        logger.setLevel(logging.CRITICAL)

def main():
    config = Config()
    log_level = logging.INFO
    try:
        cfg_console_log_level = config.get("GENERAL", "CONSOLE_LOG_LEVEL")
    except:
        cfg_console_log_level = "Critical"

    try:
        cfg_file_log_level = config.get("GENERAL", "FILE_LOG_LEVEL")
    except:
        cfg_file_log_level = "Info"

    stormberry_logger = logging.getLogger('stormberry-station')
    stormberry_logger.setLevel(logging.DEBUG)

    yapsy_logger = logging.getLogger('yapsy')
    yapsy_logger.setLevel(logging.DEBUG)

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
    termhandler = logging.StreamHandler(sys.stdout)
    termhandler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s][%(name)s]:%(message)s",
            "%Y-%m-%d %H:%M:%S")
    filehandler.setFormatter(formatter)
    termhandler.setFormatter(formatter)

    stormberry_logger.addHandler(filehandler)
    stormberry_logger.addHandler(termhandler)

    yapsy_logger.addHandler(filehandler)
    yapsy_logger.addHandler(termhandler)

    set_handler_level_from_str(filehandler, cfg_file_log_level)
    set_handler_level_from_str(termhandler, cfg_console_log_level)

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
