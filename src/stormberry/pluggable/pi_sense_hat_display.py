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
from sense_hat import SenseHat, ACTION_RELEASED, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT, ACTION_PRESSED, DIRECTION_MIDDLE
from threading import Timer

import datetime
import logging
import os
import sys
import time

from stormberry.config import Config
from stormberry.util.containers import CarouselContainer
from stormberry.weather_reading import WeatherReading

from stormberry.plugin import IDisplayPlugin

class RPiSenseHatDisplay(IDisplayPlugin, CarouselContainer):

    def __init__(self):

        super(IDisplayPlugin, self).__init__()
        self._sense_hat = None
        self._latest_reading = None

    def activate(self, config):
        """Activates sensors by requesting first values and assigning handlers."""
        self.config = config

        self._sense_hat = data_manager.get_entity('pi-sense-hat')
        if self._sense_hat is None:
            self._sense_hat = SenseHat()
            data_manager.store_entity('pi-hat', self._sense_hat)

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
        self._sense_hat.stick.direction_middle = self._toggle_display

        """Launches multiple threads to handle configured behavior."""
        if self.config.getboolean("GENERAL", "UPDATE_DISPLAY") and self.config.getint("GENERAL", "UPDATE_INTERVAL"):
            self._update_display()

        return True

    def deactivate(self):
        """Tries to stop active threads and clean up screen."""
        if self._sense_hat:
            self._sense_hat.clear()

    @property
    def carousel_items(self):
        return DEFAULT_WEATHER_ENTITIES

    @property
    def current_style(self):
        return self.current_item.current_style

    @property
    def latest_reading(self):
        return self._latest_reading

    def _toggle_display(self, event):
        if event.action == ACTION_RELEASED:
            self._sense_hat.clear()
            if event.direction == DIRECTION_MIDDLE:
                old_update_display = self.config.getboolean("GENERAL", "UPDATE_DISPLAY")
                new_update_display = not old_update_display
                self.config.set("GENERAL", "UPDATE_DISPLAY", str(new_update_display))

        self._update_display(loop=False)

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

    def _show_message(self, message, message_color=(255,255,255), background_color=(0, 0, 0)):
        """Internal. Shows message by scrolling it over HAT screen."""
        # Need to be sure we revert any changes to rotation
        self._sense_hat.rotation = 0
        self._sense_hat.show_message(message, self.config.getfloat("GENERAL", "SCROLL_TEXT_SPEED"), message_color, background_color)

    def update(self, weather_reading):
        """Internal. Continuously updates screen with new sensors values."""

        sensors_data = weather_reading

        if sensors_data is not None:
            if self.current_item.entity_type is WeatherEntityType.TEMPERATURE:
                pixels = self.current_item.show_pixels(sensors_data.tempc)
            elif self.current_item.entity_type is WeatherEntityType.HUMIDITY:
                pixels = self.current_item.show_pixels(sensors_data.humidity)
            else:
                pixels = self.current_item.show_pixels(sensors_data.pressure_inHg)

            self._sense_hat.set_rotation(self.current_style.rotation)
            self._sense_hat.set_pixels(pixels)

            self._latest_reading = sensors_data


class VisualStyle(object):
    """Base class for all visual styles."""
    __metaclass__ = ABCMeta

    def __init__(self, positive_color, negative_color):
        # No color for led
        self._e = (0, 0, 0)

        # We use positive and negative color tuples to figure out the color applied to visual style
        # For example:
        #   +23 Celsius is shown as 23 in red color
        #   -15 Celsius is shown as 15 in blue color
        self._p = positive_color
        self._n = negative_color

    @property
    def rotation(self):
        """Rotation to be applied to a pixel map."""
        return 0

    @abstractmethod
    def apply_style(self, value):
        """Applies style for given value."""
        pass

class ArrowStyle(VisualStyle):
    """
    Arrow visual style implementation.

    Depends on previous and new values:
        a) if new/current value is bigger than previous shows arrow up
        b) if new/current values is less than previous shows arrow down
        c) if values are equal shows equals symbol
    """

    def __init__(self, positive_color, negative_color):
        super(ArrowStyle, self).__init__(positive_color, negative_color)

        # Previous value to be used for style render
        self._previous_value = 0

        # Arrow up pixels map
        self._arrow_up = (
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e, #0
            self._e, self._e, self._p, self._p, self._p, self._p, self._e, self._e, #1
            self._e, self._p, self._e, self._p, self._p, self._e, self._p, self._e, #2
            self._p, self._e, self._e, self._p, self._p, self._e, self._e, self._p, #3
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e, #4
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e, #5
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e, #6
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e  #7
        )

        # Arrow down pixels map
        self._arrow_down = tuple(self._n if pixel is self._p else self._e for pixel in self._arrow_up[::-1])

        # Equals symbol pixels map
        self._equals = (
            self._e, self._e, self._e, self._e, self._e, self._e, self._e, self._e, #0
            self._e, self._e, self._e, self._e, self._e, self._e, self._e, self._e, #1
            self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p, #2
            self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p, #3
            self._n, self._n, self._n, self._n, self._n, self._n, self._n, self._n, #4
            self._n, self._n, self._n, self._n, self._n, self._n, self._n, self._n, #5
            self._e, self._e, self._e, self._e, self._e, self._e, self._e, self._e, #6
            self._e, self._e, self._e, self._e, self._e, self._e, self._e, self._e, #7
        )

    def apply_style(self, value):
        # Need delta of current and previous values to figure what symbol to show
        new_value = value
        new_value -= self._previous_value
        self._previous_value = value

        # If no changes, show equals symbol
        if not new_value:
            return self._equals

        return self._arrow_up if new_value > 0 else self._arrow_down

class NumericStyle(VisualStyle):
    """
    Numeric visual style implementation.

    Shows one/two digits values.
    In case value has more than 2 digits shows infinity symbol.
    """

    def __init__(self, positive_color, negative_color):
        super(NumericStyle, self).__init__(positive_color, negative_color)

        # Empty line, used to build final number
        self._empty_line = (self._e, self._e, self._e, self._e, self._e, self._e, self._e, self._e)

        # Numbers dictionary: key is number as string, value is its pixel map
        self._numbers = {
            '0': (
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
                self._p, self._e, self._e, self._e, self._e, self._e, self._e, self._p,
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
            ),
            '1': (
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
                self._e, self._p, self._e, self._e, self._e, self._e, self._e, self._e,
                self._e, self._e, self._p, self._e, self._e, self._e, self._e, self._e,
            ),
            '2': (
                self._p, self._p, self._p, self._p, self._p, self._e, self._e, self._p,
                self._p, self._e, self._e, self._e, self._p, self._e, self._e, self._p,
                self._p, self._e, self._e, self._e, self._p, self._p, self._p, self._p,
            ),
            '3': (
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
                self._p, self._e, self._e, self._e, self._p, self._e, self._e, self._p,
                self._p, self._e, self._e, self._e, self._p, self._e, self._e, self._p,
            ),
            '4': (
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
                self._e, self._e, self._e, self._e, self._p, self._e, self._e, self._e,
                self._p, self._p, self._p, self._p, self._p, self._e, self._e, self._e,
            ),
            '5': (
                self._p, self._e, self._e, self._e, self._p, self._p, self._p, self._p,
                self._p, self._e, self._e, self._e, self._p, self._e, self._e, self._p,
                self._p, self._p, self._p, self._p, self._p, self._e, self._e, self._p,
            ),
            '6': (
                self._p, self._e, self._e, self._e, self._p, self._p, self._p, self._p,
                self._p, self._e, self._e, self._e, self._p, self._e, self._e, self._p,
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
            ),
            '7': (
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
                self._p, self._e, self._e, self._e, self._e, self._e, self._e, self._e,
                self._p, self._e, self._e, self._e, self._e, self._e, self._e, self._e,
            ),
            '8': (
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
                self._p, self._e, self._e, self._e, self._p, self._e, self._e, self._p,
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
            ),
            '9': (
                self._p, self._p, self._p, self._p, self._p, self._p, self._p, self._p,
                self._p, self._e, self._e, self._e, self._p, self._e, self._e, self._p,
                self._p, self._p, self._p, self._p, self._p, self._e, self._e, self._p,
            )
        }

        # Infinity symbol used for bigger than 2 digits numbers
        self._infinity = (
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e,
            self._e, self._e, self._p, self._e, self._e, self._p, self._e, self._e,
            self._e, self._e, self._p, self._e, self._e, self._p, self._e, self._e,
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e,
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e,
            self._e, self._e, self._p, self._e, self._e, self._p, self._e, self._e,
            self._e, self._e, self._p, self._e, self._e, self._p, self._e, self._e,
            self._e, self._e, self._e, self._p, self._p, self._e, self._e, self._e,
        )

    @property
    def rotation(self):
        # We need to rotate due to specific way of building number pixel map
        return 90

    def apply_style(self, value):
        # We need to get abs as we do not show minus symbol, we use different colors for this
        # We need to round value, we show only 2 digits and 25.8 is closer to 26 from UX perspecrtive
        # We call int to make sure we use integer rather than float
        # We call str to convert 2 digits number to string for futher parsing
        str_value = str(int(round(abs(value))))

        # If number is 2 digits build 2 digits pixel map
        if len(str_value) == 2:
            result = list(self._numbers[str_value[1]]) #0-2
            result += self._empty_line * 2             #3-4
            result += self._numbers[str_value[0]]      #5-7
        # If number is one digit show one digit pixel map
        elif len(str_value) == 1:
            result = list(self._empty_line * 2)        #0-1
            result += self._numbers[str_value]         #2-4
            result += self._empty_line * 3             #5-7
        # Or show infinity symbol
        else:
            result = self._infinity

        # Figure out what color to use depending on positive or negative value
        if value <= 0:
            result = tuple(self._n if pixel is self._p else self._e for pixel in result)

        return result

class SquareStyle(VisualStyle):
    """
    Square visual style implementation.

    Visualize value as a square of different colored pixels.
    """

    def __init__(self, positive_color, negative_color):
        super(SquareStyle, self).__init__(positive_color, negative_color)

    def apply_style(self, value):
        # Depending on value we use positive or negative color to fill pixels.
        # We use range of 64 because the screen resolution is 8x8
        if value > 0:
            return tuple(self._p if i < value else self._n for i in range(64))

        return tuple(self._n if i < -value else self._p for i in range(64))

class WeatherEntityType(object):
    """Enum object for weather enitites types."""
    HUMIDITY, PRESSURE, TEMPERATURE = range(3)

class WeatherEntity(CarouselContainer):
    """Base class for weather entities implementations."""
    __metaclass__ = ABCMeta

    def __init__(self, config=None):
        self.config = config if config is not None else Config()
        super(WeatherEntity, self).__init__()

        # Default set of visual styles for weather entity instance
        self._visual_styles = (
            NumericStyle(self.positive_color, self.negative_color),
            ArrowStyle(self.positive_color, self.negative_color),
            SquareStyle(self.positive_color, self.negative_color)
        )

    @abstractproperty
    def entity_messsage(self):
        """Message to show when switching to it."""
        pass

    @abstractproperty
    def positive_color(self):
        """Color to use for positive values."""
        pass

    @abstractproperty
    def negative_color(self):
        """Color to use for negative values."""
        pass

    @abstractproperty
    def entity_type(self):
        """Returns WeatherEntityType value."""
        pass

    @property
    def carousel_items(self):
        return self._visual_styles

    @property
    def current_style(self):
        """Current applied visual style."""
        return self.current_item

    def show_pixels(self, value):
        """Shows pixel for current entity and applied visual style."""
        return self.current_item.apply_style(value)

class HumidityEntity(WeatherEntity):
    """Humidity enity implementation."""

    def __init__(self):
        super(HumidityEntity, self).__init__()

    @property
    def entity_messsage(self):
        return 'Humidity'

    @property
    def positive_color(self):
        return self.config.getinttuple('GENERAL', 'HUM_POSITIVE')

    @property
    def negative_color(self):
        return self.config.getinttuple('GENERAL', 'HUM_NEGATIVE')

    @property
    def entity_type(self):
        return WeatherEntityType.HUMIDITY

    def show_pixels(self, value):
        # For square visual style we divide by 100 and multiply by 64 (8x8 screen resolution)
        # because humidity value is in percent
        if self.current_style is SquareStyle:
            value = 64 * value / 100

        return super(HumidityEntity, self).show_pixels(value)

class PressureEntity(WeatherEntity):
    """Pressure enity implementation."""

    def __init__(self):
        super(PressureEntity, self).__init__()

    @property
    def entity_messsage(self):
        return 'Pressure'

    @property
    def positive_color(self):
        return self.config.getinttuple('GENERAL', 'PRESS_POSITIVE')

    @property
    def negative_color(self):
        return self.config.getinttuple('GENERAL', 'PRESS_NEGATIVE')

    @property
    def entity_type(self):
        return WeatherEntityType.PRESSURE

class TemperatureEntity(WeatherEntity):
    """Temperature enity implementation."""

    def __init__(self):
        super(TemperatureEntity, self).__init__()

    @property
    def entity_messsage(self):
        return 'Temperature'

    @property
    def positive_color(self):
        return self.config.getinttuple('GENERAL', 'TEMP_POSITIVE')

    @property
    def negative_color(self):
        return self.config.getinttuple('GENERAL', 'TEMP_NEGATIVE')

    @property
    def entity_type(self):
        return WeatherEntityType.TEMPERATURE

# Predefined weather entities tuple
DEFAULT_WEATHER_ENTITIES = (TemperatureEntity(), HumidityEntity(), PressureEntity())
