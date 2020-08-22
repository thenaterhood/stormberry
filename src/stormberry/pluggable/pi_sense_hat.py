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
from sense_hat import SenseHat

import datetime
import logging
import os
import sys
import time

from stormberry.weather_reading import WeatherReading
from stormberry.smoother import Smoother

import stormberry.plugin

class RPiSenseHat(stormberry.plugin.ISensorPlugin):

    # Constants
    SMOOTH_READINGS_NUMBER = 3

    def __init__(self):

        self._sense_hat = None
        self._latest_reading = None
        self._temp_smoother = Smoother(self.SMOOTH_READINGS_NUMBER)
        self._humid_smoother = Smoother(self.SMOOTH_READINGS_NUMBER)
        self._last_reading = None

    def prepare(self, config, data_manager):
        """Activates sensors by requesting first values and assigning handlers."""
        self.config = config

        self._sense_hat = SenseHat()
        try:
            data_manager.store_entity('pi-sense-hat', self._sense_hat)
        except:
            self._sense_hat = data_manager.get_entity('pi-sense-hat')

        # Init sensors, to be sure first effective run uses correct sensors values
        self._sense_hat.get_humidity()
        self._sense_hat.get_pressure()

        return True

    def shutdown(self):
        """Tries to stop active threads and clean up screen."""
        if self._sense_hat:
            self._sense_hat.clear()

    def get_reading(self):
        """
        Retrieves data from the sensors and returns a
        WeatherReading instance that contains it. This also
        saves the temperature for data smoothing unless
        told otherwise.

        Params:
            smooth (bool): whether to smooth sensor values.
                defaults to true. If false, the value will
                not be smoothed and will not be kept for
                future smoothing.
        """
        temp_in_celsius = self._get_temperature()
        humidity = self._get_humidity()

        # Average out value across the last three readings
        if (self._last_reading is None):
            temp_in_celsius = self._temp_smoother.smooth(temp_in_celsius)
            humidity = self._humid_smoother.smooth(humidity)

        wr = WeatherReading(
                tempc=temp_in_celsius,
                humidity=humidity,
                pressureMillibars=self._sense_hat.get_pressure(),
                date=datetime.datetime.now()
                )

        self._last_reading = wr
        return wr

    def get_health(self):
        return True

    def _get_temperature(self):
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

        if (self.config.getboolean("GENERAL", "ADJUST_TEMPERATURE_FOR_CPU")):
            # Get the CPU temperature
            cpu_temp = self._get_cpu_temp()
            # Calculate temperature compensating for CPU heating
            try:
                correction_factor = self.config.getfloat("GENERAL", "CPU_TEMP_FACTOR")
            except:
                correction_factor = 5.466

            adj_temp = avg_temp - ((cpu_temp - avg_temp) / correction_factor)
        else:
            adj_temp = avg_temp

        adj_temp = adj_temp * self.config.getfloat("GENERAL", "TEMPERATURE_ADJUSTMENT")
        return adj_temp

    def _get_humidity(self):
        """Gets humidity sensor value."""
        return self._sense_hat.get_humidity() * self.config.getfloat("GENERAL", "HUMIDITY_ADJUSTMENT")

    def _get_pressure(self):
        """Gets humidity sensor value and converts pressure from millibars to inHg before posting."""
        return self._sense_hat.get_pressure() * self.config.getfloat("GENERAL", "PRESSURE_ADJUSTMENT")

    def _get_cpu_temp(self):
        """"
        Internal.
        Executes a command at the OS to pull in the CPU temperature.
        Thanks to https://www.raspberrypi.org/forums/viewtopic.php?f=104&t=111457
        """

        res = os.popen('vcgencmd measure_temp').readline()
        return float(res.replace('temp=', '').replace("'C\n", ''))

