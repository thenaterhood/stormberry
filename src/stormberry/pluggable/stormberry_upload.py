"""
Stormberry uploading plugin, intended for use with stormberry server

This is designed for use in situations where the station and the server
are running on different things.
"""
import logging
import urllib.error
from urllib.parse import urlencode
from urllib.request import Request

import stormberry.plugin


class StormberryUpload(stormberry.plugin.IRepositoryPlugin):
    """StormberryUpload plugin"""

    def prepare(self, config, data_manager):
        self.config = config
        self.data_manager = data_manager
        return True

    def store_reading(self, reading):

        previous_values = self.data_manager.get_entity('readings_pending_upload')
        self.data_manager.del_entity('readings_pending_upload')

        if previous_values is None:
            previous_values = []

        previous_values.append(reading)
        still_pending_readings = []

        for v in previous_values:
            try:
                endpoint = self.config.get('STORMBERRY_UPLOAD', 'URL')
                token = self.config.get('STORMBERRY_UPLOAD', 'TOKEN')
            except:
                logging.error("stormberry upload is not configured")
                # There's nothing we can do here and retrying isn't helpful
                # because we have no configuration
                return False

            request_reading = v.dict
            request_reading['token'] = token

            request = Request(endpoint, urlencode(request_reading).encode())
            try:
                urllib.request.urlopen(request)
            except urllib.error.URLError as e:
                still_pending_readings.append(v)
                logging.warning("stormberry upload failed: " + str(e.reason))
                break

        self.data_manager.store_entity('readings_pending_upload', still_pending_readings)
        return True
