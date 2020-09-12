import stormberry.plugin
from stormberry.weather_reading import WeatherReading

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

from bme280 import BME280

# See https://github.com/pimoroni/enviroplus-python
# pip3 install enviroplus
# Enable i2c. This assumes a "modern" pi which uses port 1.

class BME280_I2C(stormberry.plugin.ISensorPlugin):

    def prepare(self, config, data_manager):

        self.data_manager = data_manager
        self.config = config
        self.bus = SMBus(1)
        self.bme280 = BME280(i2c_dev=self.bus)
        self.cpu_temps = [self.get_cpu_temperature()] * 5
        try:
            self.compensate_temp = self.config.getboolean("BME280", "CPU_COMPENSATE")
        except:
            self.compensate_temp = True

        try:
            self.compensate_temp_factor = self.config.getint("BME280", "CPU_COMPENSATION_FACTOR")
        except:
            self.compensate_temp_factor = 2.25

    def get_reading(self):

        try:
            tempc = self.bme280.get_temperature()
            if self.compensate_temp:
                tempc = self.compensate_temperature(tempc)

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

    def get_cpu_temperature(self):
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = f.read()
            temp = int(temp) / 1000.0
        return temp

    def compensate_temperature(self, raw_temp):
        # Based on code from https://github.com/pimoroni/enviroplus-python/blob/master/examples/compensated-temperature.py
        self.cpu_temps = self.cpu_temps[1:] + [self.get_cpu_temperature()]
        avg_cpu_temp = sum(self.cpu_temps) / float(len(self.cpu_temps))
        comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / self.compensate_temp_factor)
        return comp_temp

