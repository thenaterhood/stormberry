from datetime import datetime
import math


class WeatherReading():

    READINGS_PRINT_TEMPLATE = 'Temp: %sC (%sF), Humidity: %s%%, Pressure: %s inHg, Wind MPH: %s'

    def __init__(
            self,
            tempc=None,
            humidity=None,
            pressureMillibars=None,
            date=None,
            pressureInchesHg=None,
            wind_mph=None,
            pm_2_5=None,
            pm_10=None,
            precipitation_cm=None,
            noise_dB=None,
            pressure_hectopascal=None,
            wet_bulb_temp_c=None,
            globe_temp_c=None
            ):

        self.__reading = dict()

        if pressureMillibars is not None:
            self.__pressure = pressureMillibars
        elif pressureInchesHg is not None:
            self.__pressure = pressureInchesHg / 0.029530
        elif pressure_hectopascal is not None:
            # yes, these are equal
            self.__pressure = pressure_hectopascal
        else:
            self.__pressure = None

        self.__tempc = tempc
        self.__humidity = humidity
        self.__date = date if date is not None else datetime.now()
        self.__wind_mph = wind_mph
        self.__pm_2_5 = pm_2_5
        self.__pm_10 = pm_10
        self.__precipitation_cm = precipitation_cm
        self.__noise_dB = noise_dB
        self.__wet_bulb_temp_c = wet_bulb_temp_c
        self.__globe_temp_c = globe_temp_c

    @property
    def globe_temp_c(self):
        return self.__globe_temp_c

    @property
    def wet_bulb_temp_c(self):
        if self.__wet_bulb_temp_c is not None:
            return self.__wet_bulb_temp_c

        if self.__humidity is None or self.__tempc is None:
            return None

        # From https://www.weather.gov/media/tsa/pdf/WBGTpaper2.pdf
        return (-5.806 + 0.672 * self.tempc - 0.006 * (self.tempc**2) +(0.061 + 0.004 * self.tempc + 99*(10**-6) * (self.tempc**2)) * self.humidity + (-33*(10**-6) -5*(10**-6) *self.tempc-1*(10**-7) * (self.tempc**2)) * (self.humidity**2))

    @property
    def wet_bulb_globe_temp_c(self):
        '''
        This is generally calculated rather than directly measured because
        the equipment to measure it is expensive.
        '''
        wet_bulb = self.wet_bulb_temp_c
        if wet_bulb is None:
            return None

        if self.tempc is None:
            return None

        if self.globe_temp_c is None:
            return (0.7 * wet_bulb + 0.3 * self.tempc)
        else:
            return (0.7 * wet_bulb + 0.2 * self.globe_temp_c + 0.1*self.tempc)

    @property
    def noise_dB(self):
        return self.__noise_dB

    @property
    def precipitation_cm(self):
        return self.__precipitation_cm

    @property
    def pm_2_5(self):
        return self.__pm_2_5

    @property
    def pm_10(self):
        return self.__pm_10

    @property
    def tempc(self):
        if self.__tempc is None:
            return None

        return round(self.__tempc, 2)

    @property
    def tempf(self):
        if self.__tempc is None:
            return None

        return self.ctof(self.tempc)

    @property
    def pressure_millibars(self):
        if self.__pressure is None:
            return None

        return round(self.__pressure, 2)

    @property
    def pressure_inHg(self):
        if self.__pressure is None:
            return None

        return round(self.__pressure * 0.0295300, 2)

    @property
    def humidity(self):
        if self.__humidity is None:
            return None

        return round(self.__humidity, 2)

    @property
    def timestamp(self):
        return self.__date

    @property
    def timestr(self):
        if self.__date is None:
            return None

        return self.__date.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def dewpointc(self):
        """
        Calculates dewpoint in celsius, uses simplified formula less accurate but obvious.
        https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
        """
        if self.__tempc is None or self.__humidity is None:
            return None

        return self.__tempc - (100 - self.__humidity) / 5

    @property
    def dewpointf(self):
        if self.__humidity is None or self.tempf is None:
            return None

        return self.tempf - (100 - self.__humidity) / 5

    @property
    def humidex_c(self):
        if self.humidity is None or self.dewpointc is None:
            return None

        t = self.tempc
        d = self.dewpointc
        # Approximation of math constant e
        e = 2.71828

        humidex = t + 0.5555 * (6.11* math.exp(5417.7530*(1/273.16 - 1/(273.15+d)))-10)

        return humidex

    @property
    def heat_index_c(self):
        # Formula is from https://en.wikipedia.org/wiki/Heat_index
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -6.83783e-3
        c6 = -5.481717e-2
        c7 = 1.22874e-3
        c8 = 8.5282e-4
        c9 = -1.99e-6
        t = self.tempf
        r = self.humidity

        if t is None or r is None:
            return None

        # Below 80, the heat index is not valid using this equation
        if (t < 80):
            return None

        heat_index = math.fsum([
            c1,
            c2*t,
            c3*r,
            c4*t*r,
            c5*(t**2),
            c6*(r**2),
            c7*r*(t**2),
            c8*t*(r**2),
            c9*(t**2)*(r**2)
            ])

        return self.ftoc(heat_index)

    @property
    def wind_mph(self):
        return self.__wind_mph

    def windchill_c(self):
        t = self.tempf
        if t is None:
            return None

        if self.wind_mph is not None:
            v = self.wind_mph
        else:
            v = 3.5 # average walking speed, assuming no other wind

        windchill = 35.74 + 0.6215*t - 35.75*(v**0.16) + 0.4275*t*(v**0.16)

        # If windchill calculates to higher than the air temperature,
        # the equation is not valid for our conditions.
        if windchill > t:
            return None
        else:
            return self.ftoc(windchill)

    @property
    def tuple(self):
        return (
                self.tempc,
                self.tempf,
                self.humidity,
                self.pressure_inHg,
                self.wind_mph,
                self.pm_2_5,
                self.pm_10,
                self.precipitation_cm,
                self.noise_dB
                )

    @property
    def dict(self):
        return {
                'timestr': self.timestr,
                'datetime': self.__date,
                'tempc': self.tempc,
                'tempf': self.tempf,
                'humidity': self.humidity,
                'inchesHg' : self.pressure_inHg,
                'dewpointc': self.dewpointc,
                'dewpointf': self.dewpointf,
                'wind_mph': self.wind_mph,
                'pm_2_5': self.pm_2_5,
                "pm_10": self.pm_10,
                'precipitation_cm': self.precipitation_cm,
                'noise_dB': self.noise_dB
                }

    @property
    def fields(self):
        return self.dict.keys()

    def merge(self, weather_reading):
        self.__date = self.__date if self.__date is not None else weather_reading.timestamp
        self.__tempc = self.__tempc if self.__tempc is not None else weather_reading.tempc
        self.__humidity = self.__humidity if self.__humidity is not None else weather_reading.humidity
        self.__pressure = self.__pressure if self.__pressure is not None else weather_reading.pressure_millibars
        self.__wind_mph = self.__wind_mph if self.__wind_mph is not None else weather_reading.wind_mph
        self.__pm_2_5 = self.__pm_2_5 if self.__pm_2_5 is not None else weather_reading.pm_2_5
        self.__precipitation_cm = self.__precipitation_cm if self.__precipitation_cm is not None else weather_reading.__precipitation_cm
        self.__noise_dB = self.__noise_dB if self.__noise_dB is not None else weather_reading.noise_dB,
        self.__pm_10 = self.__pm_10 if self.__pm_10 is not None else weather_reading.pm_10
        self.__wet_bulb_temp_c = self.__wet_bulb_temp_c if self.__wet_bulb_temp_c is not None else weather_reading.wet_bulb_temp_c

    def __str__(self):
        return (self.READINGS_PRINT_TEMPLATE % self.tuple[0:5])

    def ctof(self, celsius):
        return (celsius * 1.8) + 32

    def ftoc(self, f):
        return (f - 32) / 1.8

