import sqlite3
import os
import stormberry.plugin

class SQLite3Store(stormberry.plugin.IRepositoryPlugin):

    create_query = "CREATE TABLE IF NOT EXISTS weather_data(id INTEGER PRIMARY KEY ASC, timestr, tempc, inchesHg, humidity, dewpointc)"
    insert_query = "INSERT INTO weather_data(timestr, tempc, inchesHg, humidity, dewpointc) VALUES (:timestr, :tempc, :inchesHg, :humidity, :dewpointc)"

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
