import csv
import os
from stormberry.plugin import IRepositoryPlugin

class CSVWriter(IRepositoryPlugin):

    def activate(self, config, data_manager):
        self.config = config

    def store_reading(self, data):

        behaviour = self.config['CSV']['BEHAVIOUR']
        filename = self.config['CSV']['FILENAME']

        csv_file_exists = os.path.exists(filename)

        if csv_file_exists and behaviour == "overwrite":
            os.unlink(filename)
            csv_file_exists = False

        with open(filename, 'a') as csv_file:
            fieldnames = ["timestr", "tempc", "tempf", "humidity", "inchesHg", "dewpointc"]
            writer = csv.DictWriter(csv_file, fieldnames)

            if not csv_file_exists:
                writer.writeheader()

            writer.writerow({
                'tempc': data.tempc,
                'tempf': data.tempf,
                'timestr': data.timestr,
                'humidity': data.humidity,
                'inchesHg': data.pressure_inHg,
                'dewpointc': data.dewpointc
                })

        return True

    def health_check(self):
        return os.access(self.config['CSV']['FILENAME'], os.W_OK)
