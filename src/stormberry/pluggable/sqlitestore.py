import sqlite3
import os
import stormberry.plugin
from datetime import datetime
from stormberry.weather_reading import WeatherReading

class SQLite3Store(stormberry.plugin.IRepositoryPlugin):

    create_query = "CREATE TABLE IF NOT EXISTS weather_data(id INTEGER PRIMARY KEY ASC, timestr, tempc, inchesHg, humidity, dewpointc)"
    insert_query = "INSERT INTO weather_data(timestr, tempc, inchesHg, humidity, dewpointc) VALUES (:timestr, :tempc, :inchesHg, :humidity, :dewpointc)"

    def prepare(self, config, data_manager):

        self.config = config
        self.data_manager = data_manager
        self.db = None

        try:
            self.db = sqlite3.connect(config.get('SQLITE', 'FILENAME'))
        except:
            return False

        self.cursor = self.db.cursor()

    def shutdown(self):
        if self.db is not None:
            self.db.close()

    def store_reading(self, data, first_time=False):

        filename = self.config.get('SQLITE', 'FILENAME')

        file_exists = os.path.exists(filename)

        db = sqlite3.connect(filename)
        db.execute(self.create_query)

        insert_data = {
                'timestr': data.timestr,
                'tempc' : data.tempc,
                'dewpointc' : data.dewpointc,
                'humidity' : data.humidity,
                'inchesHg' : data.pressure_inHg
                }

        db.execute(self.insert_query, insert_data)
        db.commit()
        db.close()

        return True

    def health_check(self):
        return os.access(self.config.get('SQLITE', 'FILENAME'), os.W_OK)

    def get_latest(self):
        query = "SELECT * FROM weather_data ORDER BY ID DESC LIMIT 1"
        self.cursor.execute(query)
        return self._transform_db_row(self.cursor.fetchone())

    def get_between(self, start_time, end_time = None):
        if end_time is None:
            query = "SELECT * FROM weather_data WHERE timestr >= Datetime(?)"
            self.cursor.execute(query, (start_time,))
        else:
            query = "SELECT * FROM weather_data WHERE timestr >= Datetime(?) AND timestr <= Datetime(?)"
            self.cursor.execute(query, (start_time, end_time))

        readings = []
        for row in self.cursor:
            readings.append(self._transform_db_row(row))

        return readings

    def get_mean_between(self, start_time, end_time = None):
        if end_time is None:
            query = "SELECT AVG(tempc), AVG(humidity), AVG(dewpointc) FROM weather_data WHERE timestr >= Datetime(?)"
            self.cursor.execute(query, (start_time,))
        else:
            query = "SELECT AVG(tempc), AVG(humidity), AVG(dewpointc) FROM weather_data WHERE timestr >= Datetime(?) AND timestr <= Datetime(?)"
            self.cursor.execute(query, (start_time, end_time))
            result = self.cursor.fetchone()

        averages = {
                'tempc_avg': result[0],
                'humidity_avg': result[1],
                'dewpointc_avg': result[2]
                }

        return averages

    def get_extremes_between(self, start_time, end_time = None):
        if end_time is None:
            query = "SELECT MIN(tempc), MAX(tempc), MIN(humidity), MAX(humidity), MIN(dewpointc), MAX(dewpointc) FROM weather_data WHERE timestr >= Datetime(?)"
            self.cursor.execute(query, (start_time,))
        else:
            query = "SELECT MIN(tempc), MAX(tempc), MIN(humidity), MAX(humidity), MIN(dewpointc), MAX(dewpointc) FROM weather_data WHERE timestr >= Datetime(?) AND timestr <= Datetime(?)"
            self.cursor.execute(query, (start_time, end_time))
            result = self.cursor.fetchone()

        extremes = {
                'tempc_min': result[0],
                'tempc_max': result[1],
                'humidity_min': result[2],
                'humidity_max': result[3],
                'dewpointc_min': result[4],
                'dewpointc_max': result[5]
                }

        return extremes

    def _transform_db_row(self, row):
        timestamp = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        return WeatherReading(
                date=timestamp,
                tempc=row[2],
                pressureInchesHg=row[3],
                humidity=row[4],
            )

