from threading import Timer

import datetime
import logging
import os
import sys
import time

from stormberry.config import Config
from stormberry.plugin import PluginDataManager
from stormberry.plugin.manager import PluginTypeName, get_plugin_manager
from stormberry.weather_reading import WeatherReading


class WeatherStation():

    def __init__(self, plugin_manager=None, config=None, plugin_data_manager=None, log=None):

        self._periodic_timer = None
        self.log = log if log is not None else logging
        self.config = config if config is not None else Config()
        self.plugin_data_manager = plugin_data_manager if plugin_data_manager is not None else PluginDataManager()
        self.plugin_manager = plugin_manager if plugin_manager is not None else get_plugin_manager(self.config)
        self._latest_reading = None

    def prepare_sensors(self):
        for sensor in self.plugin_manager.getPluginsOfCategory(PluginTypeName.SENSOR):
            sensor.plugin_object.prepare(self.config, self.plugin_data_manager)

    def prepare_repositories(self):
        for repo in self.plugin_manager.getPluginsOfCategory(PluginTypeName.REPOSITORY):
            repo.plugin_object.prepare(self.config, self.plugin_data_manager)

    def prepare_displays(self):
        if self.config.getboolean("GENERAL", "ENABLE_DISPLAY"):
            for display in self.plugin_manager.getPluginsOfCategory(PluginTypeName.DISPLAY):
                display.plugin_object.prepare(self.config, self.plugin_data_manager)

    def start_station(self):
        """Launches multiple threads to handle configured behavior."""
        self._periodic_callback()

    def stop_station(self, *arg):
        """Tries to stop active threads and clean up screen."""
        for plugin in self.plugin_manager.getAllPlugins():
            plugin.plugin_object.shutdown()

        if self._periodic_timer:
            self._periodic_timer.cancel()

    def take_reading(self):
        final_reading = WeatherReading()

        for sensor in self.plugin_manager.getPluginsOfCategory(PluginTypeName.SENSOR):
            if self._latest_reading is not None and sensor.plugin_object.in_operating_range(self._latest_reading):
                self.log.info("Sensor plugin %s reports we're outside operating range. Skipping." % str(sensor.plugin_object.__class__.__name__))
                continue

            reading = sensor.plugin_object.get_reading()
            if reading is not None:
                final_reading.merge(reading)

        self.log.debug("New reading: " + str(final_reading))
        return final_reading

    def report_reading(self, reading):

        if self.config.getboolean("GENERAL", "ENABLE_DISPLAY"):
            for display in self.plugin_manager.getPluginsOfCategory(PluginTypeName.DISPLAY):
                display.plugin_object.update(reading)

        if self._latest_reading is None and self.config.getboolean("GENERAL", "DISCARD_FIRST_READING"):
            return

        for repo in self.plugin_manager.getPluginsOfCategory(PluginTypeName.REPOSITORY):
            repo.plugin_object.store_reading(reading)

    def _periodic_callback(self):

        wr = self.take_reading()
        self.report_reading(wr)

        self._latest_reading = wr

        self._periodic_timer = self._start_timer(self.config.getint("GENERAL", "UPDATE_INTERVAL"), self._periodic_callback)

    def _start_timer(self, interval, callback):
        """Internal. Starts timer with given interval and callback function."""

        timer = Timer(interval, callback)
        timer.daemon = True
        timer.start()

        return timer

    def _get_cpu_temp(self):
        """"
        Internal.
        Executes a command at the OS to pull in the CPU temperature.
        Thanks to https://www.raspberrypi.org/forums/viewtopic.php?f=104&t=111457
        """

        res = os.popen('vcgencmd measure_temp').readline()
        return float(res.replace('temp=', '').replace("'C\n", ''))

