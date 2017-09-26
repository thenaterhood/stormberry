import logging
from storage_strategy import GenericStorageStrategy


class Echoer(GenericStorageStrategy):

    def save_data(self, data, first_time=False):

        formatstr = "Temp: %sC (%sF), Humidity: %s%%, Pressure: %s inHg"
        print(formatstr % (data.tempc, data.tempf, data.humidity, data.pressure_inHg))
