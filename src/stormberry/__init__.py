#!/usr/bin/python
'''*****************************************************************************************************************
    Raspberry Pi + Raspbian Weather Station
    By Uladzislau Bayouski
    https://www.linkedin.com/in/uladzislau-bayouski-a7474111b/

    A Raspberry Pi based weather station that measures temperature, humidity and pressure using
    the Astro Pi Sense HAT then uploads the data to a Weather Underground weather station.
    Calculates dew point. Completely configurable and working asyncroniously in multi threads. 
    Uses stick for choosing different weather entities and visual styles. 
    Uses logger to log runtime issues/errors.
    
    Inspired by http://makezine.com/projects/raspberry-pi-weather-station-mount/ project
********************************************************************************************************************'''
from __future__ import print_function
from collections import deque
from sense_hat import SenseHat, ACTION_RELEASED, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT
from threading import Timer

import datetime
import logging 
import os
import sys
import time

from stormberry.config import Config
from stormberry.weather_entities import DEFAULT_WEATHER_ENTITIES, CarouselContainer, WeatherEntityType
from stormberry.weather_reading import WeatherReading

class WeatherStation(CarouselContainer):
    """Weather Station controlling class, setups and manages station run time."""

    # Constants
    SMOOTH_READINGS_NUMBER = 3
    READINGS_PRINT_TEMPLATE = 'Temp: %sC (%sF), Humidity: %s%%, Pressure: %s inHg'

    def __init__(self, plugin_manager=None, config=None):
        super(WeatherStation, self).__init__()

        self._sense_hat = None
        self._log_timer = None
        self._upload_timer = None
        self._update_timer = None
        self._last_readings = None
        self.plugin_manager = plugin_manager
        self.config = config if config is not None else Config()

    @property
    def carousel_items(self):
        return DEFAULT_WEATHER_ENTITIES

    @property
    def current_style(self):
        return self.current_item.current_style

    def activate_sensors(self):
        """Activates sensors by requesting first values and assigning handlers."""
        self._sense_hat = SenseHat()

        # Scroll Init message over HAT screen
        self._show_message('Init Sensors', (255, 255, 0), (0, 0, 255))

        # Init sensors, to be sure first effective run uses correct sensors values
        self._sense_hat.get_humidity()
        self._sense_hat.get_pressure()

        # Setup Sense Hat stick
        self._sense_hat.stick.direction_up = self._change_weather_entity
        self._sense_hat.stick.direction_down = self._change_weather_entity
        self._sense_hat.stick.direction_left = self._change_weather_entity
        self._sense_hat.stick.direction_right = self._change_weather_entity
    
    def start_station(self):
        """Launches multiple threads to handle configured behavior."""
        if self.config.getboolean("GENERAL", "LOG_TO_CONSOLE") \
            and self.config.getboolean("GENERAL", "LOG_INTERVAL"):
            self._log_results(first_time=True)

        if self.config.getboolean("GENERAL", "WEATHER_UPLOAD") and self.config.getint("GENERAL", "UPLOAD_INTERVAL"):
            self._upload_results(first_time=True)

        if self.config.getboolean("GENERAL", "UPDATE_DISPLAY") and self.config.getint("GENERAL", "UPDATE_INTERVAL"):
            self._update_display()

    def stop_station(self, *args):
        """Tries to stop active threads and clean up screen."""
        if self._sense_hat:
            self._sense_hat.clear()

        if self._log_timer:
            self._log_timer.cancel()

        if self._upload_timer:
            self._upload_timer.cancel()

        if self._update_timer:
            self._update_timer.cancel()

    @staticmethod
    def calculate_dew_point(temp, hum):
        """
        Calculates dewpoint in celsius, uses simplified formula less accurate but obvious.
        https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
        """
        return temp - (100 - hum) / 5

    def get_temperature(self):
        """
        Gets temperature and adjusts it with environmental impacts (like cpu temperature).
                
        There are some issues, getting an accurate temperature reading from the
        Sense HAT is improbable, see here:
        https://www.raspberrypi.org/forums/viewtopic.php?f=104&t=111457
        We need to take CPU temp into account. The Pi foundation recommendeds using the following:
        http://yaab-arduino.blogspot.co.uk/2016/08/accurate-temperature-reading-sensehat.html        
        """
        
        # Get temp readings from both sensors
        humidity_temp = self._sense_hat.get_temperature_from_humidity()
        pressure_temp = self._sense_hat.get_temperature_from_pressure()
        
        # avg_temp becomes the average of the temperatures from both sensors
        # We need to check for pressure_temp value is not 0, to not ruin avg_temp calculation
        avg_temp = (humidity_temp + pressure_temp) / 2 if pressure_temp else humidity_temp
        
        # Get the CPU temperature
        cpu_temp = self._get_cpu_temp()
        # Calculate temperature compensating for CPU heating
        adj_temp = avg_temp - ((cpu_temp - avg_temp) / 1.5)
        
        # Average out value across the last three readings
        return self._get_smooth(adj_temp)

    def get_humidity(self):
        """Gets humidity sensor value."""
        return self._sense_hat.get_humidity()

    def get_pressure(self):
        """Gets humidity sensor value and converts pressure from millibars to inHg before posting."""
        return self._sense_hat.get_pressure()

    def get_sensors_data(self):
        """Returns sensors data tuple."""

        temp_in_celsius = self.get_temperature()

        wr = WeatherReading(
                temp_in_celsius,
                self.get_humidity(),
                self._sense_hat.get_pressure(),
                datetime.datetime.now()
                )

        return wr

    def _change_weather_entity(self, event):
        """Internal. Switches to next/previous weather entity or next/previous visual style."""

        # We need to handle release event state
        if event.action == ACTION_RELEASED:
            self._sense_hat.clear()

            if event.direction == DIRECTION_UP:
                next_entity = self.next_item
                self._show_message(next_entity.entity_messsage, next_entity.positive_color)
            elif event.direction == DIRECTION_DOWN:
                previous_entity = self.previous_item
                self._show_message(previous_entity.entity_messsage, previous_entity.positive_color)
            elif event.direction == DIRECTION_LEFT:
                self.current_item.previous_item
            else:
                self.current_item.next_item

            self._update_display(loop=False)

    def _show_message(self, message, message_color, background_color=(0, 0, 0)):
        """Internal. Shows message by scrolling it over HAT screen."""

        # Need to be sure we revert any changes to rotation
        self._sense_hat.rotation = 0
        self._sense_hat.show_message(message, self.config.getfloat("GENERAL", "SCROLL_TEXT_SPEED"), message_color, background_color)

    def _log_results(self, first_time=False):
        """Internal. Continuously logs sensors values."""

        if not first_time or self.config.getboolean("GENERAL", "WEATHER_TO_CONSOLE"):
            print(self.READINGS_PRINT_TEMPLATE % self.get_sensors_data().tuple)

        self._log_timer = self._start_timer(self.config.getint("GENERAL", "LOG_INTERVAL"), self._log_results)

    def _update_display(self, loop=True):
        """Internal. Continuously updates screen with new sensors values."""

        sensors_data = self.get_sensors_data()

        if self.current_item.entity_type is WeatherEntityType.TEMPERATURE:
            pixels = self.current_item.show_pixels(sensors_data.tempc)
        elif self.current_item.entity_type is WeatherEntityType.HUMIDITY:
            pixels = self.current_item.show_pixels(sensors_data.humidity)
        else:
            pixels = self.current_item.show_pixels(sensors_data.pressure_inHg)

        self._sense_hat.set_rotation(self.current_style.rotation)
        self._sense_hat.set_pixels(pixels)

        if loop:
            self._update_timer = self._start_timer(self.config.getint("GENERAL", "UPDATE_INTERVAL"), self._update_display)

    def _upload_results(self, first_time=False):
        """Internal. Continuously uploads new sensors values to Weather Underground."""

        data = self.get_sensors_data()
        if self.plugin_manager is not None:
            for p in self.plugin_manager.getAllPlugins():
                p.plugin_object.set_config(self.config)
                p.plugin_object.save_data(data, first_time)

        self._upload_timer = self._start_timer(self.config.getint("GENERAL", "UPLOAD_INTERVAL"), self._upload_results)

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

    def _get_smooth(self, value):
        """Moving average to smooth reading."""

        # We use deque here as it is more efficient for in/out behaviour than regular list/tuple
        if not self._last_readings:
            self._last_readings = deque((value, ) * self.SMOOTH_READINGS_NUMBER, self.SMOOTH_READINGS_NUMBER)
        else:
            self._last_readings.appendleft(value)

        # Average last temperature readings
        return sum(self._last_readings) / self.SMOOTH_READINGS_NUMBER

