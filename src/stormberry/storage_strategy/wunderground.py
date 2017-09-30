import urllib2
import logging
from stormberry.storage_strategy import GenericStorageStrategy
from urllib import urlencode


class WundergroundUploader(GenericStorageStrategy):

    def save_data(self, data, first_time=False):
        """Internal. Continuously uploads new sensors values to Weather Underground."""


        if not first_time:
            print('Uploading data to Weather Underground')

            # Build a weather data object http://wiki.wunderground.com/index.php/PWS_-_Upload_Protocol
            weather_data = {
                'action': 'updateraw',
                'ID': self.config['WUNDERGROUND']['STATION_ID'],
                'PASSWORD': self.config['WUNDERGROUND']['STATION_KEY'],
                'dateutc': 'now',
                'tempf': data.tempf,
                'humidity': data.humidity,
                'baromin': data.pressure_inHg,
                'dewptf': data.dewpointf
            }

            try:
                upload_url = self.config['WUNDERGROUND']['WU_URL'] + '?' + urlencode(weather_data)
                response = urllib2.urlopen(upload_url)
                html = response.read()
                print('Server response: ', html)
                
                # Close response object
                response.close()
            except:
                print('Could not upload to Weather Underground')
                logging.warning('Could not upload to Weather Underground', exc_info=True)


