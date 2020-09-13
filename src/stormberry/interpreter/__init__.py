import math

class WeatherInterpreter:

    __slots__ = ('repo')

    def __init__(self, repo):
        self.repo = repo

    def ctof(self, celsius):
        return (celsius * 1.8) + 32

    def ftoc(self, f):
        return (f - 32) / 1.8

    def dewpoint_comfort(self):
        dewpoint_comfort_scale = {
                'oppressive': 24,
                'uncomfortable': 20,
                'muggy': 15,
                'comfortable': 10,
                'dry': 5,
                'very-dry': -100
                }
        dewpointc = self.repo.get_latest().dewpointc

        if (dewpointc >= 24):
            return 'oppressive'
        elif (dewpointc >= 20):
            return 'uncomfortable'
        elif (dewpointc >= 15):
            return 'muggy'
        elif (dewpointc >= 10):
            return 'comfortable'
        else:
            return 'very-dry'

    def comfort_safety(self):
        '''
        This is a combined interpretation using windchill, heat index,
        humidex, and the dewpoint comfort scale. It returns all of those, plus
        interpretation.
        '''
        latest_reading = self.repo.get_latest()

        humidex = latest_reading.humidex_c
        heat_index = latest_reading.heat_index_c
        windchill = latest_reading.windchill_c
        dewpoint_comfort = self.dewpoint_comfort()
        tempc = latest_reading.tempc
        wbgt = latest_reading.wet_bulb_globe_temp_c

        comfort_safety_value = wbgt
        comfort_safety_method = 'wet-bulb-globe-temperature'
        comfort_safety_str = None
        activity_safety = None
        # This is based on a combination of humidex values,
        # heat index, and this random child safety weather
        # chart: http://www.c-uphd.org/documents/wellness/weatherwatch.pdf
        if comfort_safety_value > 54:
            comfort_safety_str = 'extreme-heat'
            activity_safety = 'no'
        elif comfort_safety_value > 40:
            comfort_safety_str = 'dangerous-heat'
            activity_safety = 'no'
        elif comfort_safety_value > 33:
            comfort_safety_str = 'uncomfortable-heat'
            activity_safety = 'with-caution'
        elif comfort_safety_value > 26:
            comfort_safety_str = 'hot'
            activity_safety = 'with-caution'
        elif comfort_safety_value > 20:
            comfort_safety_str = 'comfortable'
            activity_safety = 'yes'
        elif comfort_safety_value > 4:
            comfort_safety_str = 'cool'
            activity_safety = 'yes'
        elif comfort_safety_value > -6:
            comfort_safety_str = 'cold'
            activity_safety = 'with-caution'
        elif comfort_safety_value > -6:
            comfort_safety_str = 'uncomfortable-cold'
            activity_safety = 'no'
        elif comfort_safety_value <= -6:
            comfort_safety_str = 'dangerous-cold'
            activity_safety = 'no'

        return {
                'humidex': humidex,
                'heat_index': heat_index,
                'wbgt': wbgt,
                'windchill': windchill,
                'dewpoint_comfort': dewpoint_comfort,
                'comfort_safety_str': comfort_safety_str,
                'method': comfort_safety_method,
                'comfort_safety_value': comfort_safety_value,
                'safe_to_run': activity_safety
                }

