from datetime import datetime
from random import randint
import stormberry.plugin
from stormberry.weather_reading import WeatherReading


class FakeData(stormberry.plugin.ISensorPlugin):

    def get_reading(self):

        return WeatherReading(
                tempc=randint(-5, 30),
                humidity=randint(0, 100),
                pressureMillibars=randint(980, 1049),
                date=datetime.now()
            )
