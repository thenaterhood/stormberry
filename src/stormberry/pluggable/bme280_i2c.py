import stormberry.plugin
from stormberry.weather_reading import WeatherReading
import math

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
            self.compensate_hum = self.compensate_temp
        except:
            self.compensate_temp = True
            self.compensate_hum = True

        try:
            self.compensate_temp_factor = self.config.getfloat("BME280", "CPU_COMPENSATION_FACTOR")
        except:
            self.compensate_temp_factor = 2.25

        return True

    def get_reading(self):

        try:
            raw_tempc = self.bme280.get_temperature()
            raw_humidity = self.bme280.get_humidity()

            if self.compensate_temp:
                tempc = self.compensate_temperature(raw_tempc)
            else:
                tempc = raw_tempc

            if self.compensate_hum:
                humidity = self.compensate_humidity(raw_humidity, raw_tempc, tempc)
            else:
                humidity = raw_humidity

            pressure = self.bme280.get_pressure()

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

    def compensate_humidity(self, raw_hum, raw_temp, comp_temp):
        # This is based on code from https://forums.pimoroni.com/t/enviro-readings-unrealiable/12754/58

        comp_hum_slope = 0.966 # Linear Regression to adjust temperature-adjusted raw relative humidity to provide compensated relative humidity
        comp_hum_intercept = 15.686

        dew_point = (243.04 * (math.log(raw_hum / 100) + ((17.625 * raw_temp) / (243.04 + raw_temp)))) / (17.625 - math.log(raw_hum / 100) - (17.625 * raw_temp / (243.04 + raw_temp)))
        temp_adjusted_hum = 100 * (math.exp((17.625 * dew_point)/(243.04 + dew_point)) / math.exp((17.625 * comp_temp) / (243.04 + comp_temp)))
        comp_hum = comp_hum_slope * temp_adjusted_hum + comp_hum_intercept

        return comp_hum


