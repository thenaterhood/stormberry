import sqlite3
import os
from stormberry.GenericPlugin import GenericPlugin
from yapsy.IPlugin import IPlugin

class SQLite3Store(GenericPlugin, IPlugin):

    create_query = "CREATE TABLE IF NOT EXISTS weather_data(id INTEGER PRIMARY KEY ASC, timestr, tempc, inchesHg, humidity, dewpointc)"
    insert_query = "INSERT INTO weather_data(timestr, tempc, inchesHg, humidity, dewpointc) VALUES (:timestr, :tempc, :inchesHg, :humidity, :dewpointc)"

    def save_data(self, data, first_time=False):

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

