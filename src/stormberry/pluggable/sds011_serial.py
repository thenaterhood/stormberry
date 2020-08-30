import stormberry.plugin
import serial
from stormberry.weather_reading import WeatherReading


class SDS011_Serial(stormberry.plugin.ISensorPlugin):

    def prepare(self, config):

        self.config = config
        self.serial_device_name = config.get('SDS011', 'TTY')

        try:
            self.device = serial.Serial(self.serial_device_name)
        except serial.serialutil.SerialException as e:
            self.device = None

    def shutdown(self):
        if self.device is not None:
            try:
                self.device.close()
            except serial.serialutil.SerialException as e:
                pass

    def in_operating_range(self, prev_reading):

        if prev_reading.humidity >= 70:
            return False

        if prev_reading.tempc <= -20 or prev_reading.tempc >= 50:
            return False

        return True

    def get_reading(self):

        if self.device is None:
            self.prepare(self.config)

        if self.device is None:
            return None

        sensor_data = []

        for i in range(0, 10):
            data = self.device.read()
            sensor_data.append(data)

        pm_2_5 = int.from_bytes(b''.join(sensor_data[2:4]), byteorder="little")
        pm_10 = int.frombytes(b''.join(sensor_data[4:6]), byteorder="little")

        return WeatherReading(
                pm_2_5=pm_2_5,
                pm_10=pm_10
            )
