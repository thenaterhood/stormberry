class WeatherReading():

    READINGS_PRINT_TEMPLATE = 'Temp: %sC (%sF), Humidity: %s%%, Pressure: %s inHg'

    def __init__(self, tempc, humidity, pressure, date):
        self.__tempc = tempc
        self.__humidity = humidity
        self.__pressure = pressure
        self.__date = date

    @property
    def tempc(self):
        return round(self.__tempc, 2)

    @property
    def tempf(self):
        return round((self.__tempc * 1.8) + 32, 2)

    @property
    def pressure_millibars(self):
        return round(self.__pressure, 2)

    @property
    def pressure_inHg(self):
        return round(self.__pressure * 0.0295300, 2)

    @property
    def humidity(self):
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
    def tuple(self):
        return (
                self.tempc,
                self.tempf,
                self.humidity,
                self.pressure_inHg
                )

    @property
    def dict(self):
        return {
                'timestr': self.timestr,
                'tempc': self.tempc,
                'tempf': self.tempf,
                'humidity': self.humidity,
                'inchesHg' : self.pressure_inHg,
                'dewpointc': self.dewpointc
                }

    def __str__(self):
        return (self.READINGS_PRINT_TEMPLATE % self.tuple)

