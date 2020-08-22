import logging
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from stormberry.plugin import IRepositoryPlugin


class GSheetUploader(IRepositoryPlugin):
    '''
    Based on code from https://www.hackster.io/idreams/make-a-mini-weather-station-with-a-raspberry-pi-447866
    '''

    worksheet = None

    def _open_worksheet(self, keyfile, sheet):
        try:
            with open(keyfile) as k:
                json_key = json.load(k)
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                        keyfile,
                        ["https://spreadsheets.google.com/feeds"]
                        )
                gc = gspread.authorize(credentials)
                worksheet = gc.open(sheet).sheet1
                return worksheet
        except Exception as e:
            logging.error("Unable to access google sheet:" + str(e))

    def store_reading(self, data):

        if self.worksheet is None:
            self.worksheet = self._open_worksheet(
                    self.config.get("GSHEETS", "GDOCS_OAUTH_JSON"),
                    self.config.get("GSHEETS", "GDOCS_SPREADSHEET_NAME")
                    )

        try:
            self.worksheet.append_row((
                    data.timestr,
                    data.tempc,
                    data.humidity,
                    data.pressure_inHg,
                    data.dewpointc
                    ))
            return True
        except Exception as e:
            logging.warning("Error appending to google sheet: " + str(e))
            self.worksheet = None
            return False

