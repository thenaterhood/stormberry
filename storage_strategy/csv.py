import logging
from storage_strategy import GenericStorageStrategy
import csv
import os


class CSVWriter(GenericStorageStrategy):

    def save_data(self, data, first_time=False):

        behaviour = self.config['CSV']['BEHAVIOUR']
        filename = self.config['CSV']['FILENAME']

        csv_file_exists = os.path.exists(filename)

        if csv_file_exists and behaviour == "overwrite":
            os.unlink(filename)
            csv_file_exists = False

        with open(filename, 'a') as csv_file:
            fieldnames = ["timestamp", "tempc", "tempf", "humidity", "pressure_inHg", "dewpoint"]
            writer = csv.DictWriter(csv_file, fieldnames)

            if not csv_file_exists:
                writer.writeheader()

            writer.writerow({
                'tempc': data.tempc,
                'tempf': data.tempf,
                'timestamp': data.timestr,
                'humidity': data.humidity,
                'pressure_inHg': data.pressure_inHg,
                'dewpoint': data.dewpoint
                })

