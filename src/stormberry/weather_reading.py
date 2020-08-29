from datetime import datetime


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
            precipitation_cm=None,
            noise_dB=None
            ):

        self.__reading = dict()

        if pressureMillibars is not None:
            self.__pressure = pressureMillibars
        elif pressureInchesHg is not None:
            self.__pressure = pressureInchesHg / 0.029530
        else:
            self.__pressure = None

        self.__tempc = tempc
        self.__humidity = humidity
        self.__date = date if date is not None else datetime.now()
        self.__wind_mph = wind_mph
        self.__pm_2_5 = pm_2_5
        self.__precipitation_cm = precipitation_cm
        self.__noise_dB = noise_dB

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
    def tempc(self):
        if self.__tempc is None:
            return None

        return round(self.__tempc, 2)

    @property
    def tempf(self):
        if self.__tempc is None:
            return None

        return round((self.__tempc * 1.8) + 32, 2)

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
        return self.__date.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def dewpointc(self):
        """
        Calculates dewpoint in celsius, uses simplified formula less accurate but obvious.
        https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
        """
        return self.__tempc - (100 - self.__humidity) / 5

    @property
    def dewpointf(self):
        return self.tempf - (100 - self.__humidity) / 5

    @property
    def wind_mph(self):
        return self.__wind_mph

    @property
    def tuple(self):
        return (
                self.tempc,
                self.tempf,
                self.humidity,
                self.pressure_inHg,
                self.wind_mph,
                self.pm_2_5,
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
        self.__noise_dB = self.__noise_dB if self.__noise_dB is not None else weather_reading.noise_dB

    def __str__(self):
        return (self.READINGS_PRINT_TEMPLATE % self.tuple)
