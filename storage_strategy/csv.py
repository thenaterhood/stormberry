import urllib2
import logging
from urllib import urlencode


class CSVWriter():

    def store_results(self, data, first_time=False):
        """Internal. Continuously uploads new sensors values to Weather Underground."""

        sensors_data = data.tuple

        if not first_time:
            print('Uploading data to Weather Underground')

            # Build a weather data object http://wiki.wunderground.com/index.php/PWS_-_Upload_Protocol
            weather_data = {
                'action': 'updateraw',
                'ID': Config.STATION_ID,
                'PASSWORD': Config.STATION_KEY,
                'dateutc': 'now',
                'tempf': str(sensors_data[1]),
                'humidity': str(sensors_data[2]),
                'baromin': str(sensors_data[3]),
                'dewptf': str(self.to_fahrenheit(self.calculate_dew_point(sensors_data[0], sensors_data[2])))
            }

            try:
                upload_url = Config.WU_URL + '?' + urlencode(weather_data)
                response = urllib2.urlopen(upload_url)
                html = response.read()
                print('Server response: ', html)
                
                # Close response object
                response.close()
            except:
                print('Could not upload to Weather Underground')
                logging.warning('Could not upload to Weather Underground', exc_info=True)


