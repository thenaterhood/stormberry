from datetime import datetime
from random import randint
from stormberry.plugin import ISensorPlugin
from stormberry.weather_reading import WeatherReading


class FakeData(ISensorPlugin):

    def get_reading(self):

        return WeatherReading(
                tempc=randint(-5, 30),
                humidity=randint(0, 100),
                pressure=randint(980, 1049),
                date=datetime.now()
            )
