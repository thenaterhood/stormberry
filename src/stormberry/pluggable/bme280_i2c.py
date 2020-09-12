import stormberry.plugin
from stormberry.weather_reading import WeatherReading

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

from bme280 import BME280

# See https://github.com/pimoroni/enviroplus-python
# pip3 install enviroplus

class BME280_I2C(stormberry.plugin.ISensorPlugin):

    def prepare(self, config, data_manager):

        self.data_manager = data_manager
        self.config = config
        self.bus = SMBus(1)
        self.bme280 = BME280(i2c_dev=self.bus)

    def get_reading(self):

        try:
            tempc = self.bme280.get_temperature()
            pressure = self.bme280.get_pressure()
            humidity = self.bme280.get_humidity()

            wr = WeatherReading(
                    tempc=tempc,
                    humidity=humidity,
                    pressure_hectopascal=pressure
                    )
            return wr
        except Exception as e:
            print(e)
            return None

