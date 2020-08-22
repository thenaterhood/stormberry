import urllib2
import logging
import stormberry.plugin
from urllib import urlencode


class WundergroundUploader(stormberry.plugin.IRepositoryPlugin):

    def store_reading(self, data):
        """Internal. Continuously uploads new sensors values to Weather Underground."""


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
            return True
        except:
            print('Could not upload to Weather Underground')
            logging.warning('Could not upload to Weather Underground', exc_info=True)
            return False


