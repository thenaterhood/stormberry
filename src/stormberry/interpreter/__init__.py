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

    def heat_index(self):
        weather_reading = self.repo.get_latest()

        # Formula is from https://en.wikipedia.org/wiki/Heat_index
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -6.83783e-3
        c6 = -5.481717e-2
        c7 = 1.22874e-3
        c8 = 8.5282e-4
        c9 = -1.99e-6
        t = self.ctof(weather_reading.tempc)
        r = weather_reading.humidity
        # Below 80, the heat index is not valid using this equation
        if (t < 80):
            return None

        heat_index = math.fsum([
            c1,
            c2*t,
            c3*r,
            c4*t*r,
            c5*(t**2),
            c6*(r**2),
            c7*r*(t**2),
            c8*t*(r**2),
            c9*(t**2)*(r**2)
            ])

        return self.ftoc(heat_index)

    def windchill(self):
        latest_reading = self.repo.get_latest()
        t = self.ctof(latest_reading.tempc)
        if latest_reading.wind_mph is not None:
            v = latest_reading.wind_mph
        else:
            v = 1
        windchill = 35.74 + 0.6215*t - 35.75*(v**0.16) + 0.4275*t*(v**0.16)

        # If windchill calculates to higher than the air temperature,
        # the equation is not valid for our conditions.
        if windchill > t:
            return None
        else:
            return self.ftoc(windchill)

    def humidex(self):
        latest_reading = self.repo.get_latest()
        t = latest_reading.tempc
        d = latest_reading.dewpointc
        # Approximation of math constant e
        e = 2.71828

        humidex = t + 0.5555 * (6.11* math.exp(5417.7530*(1/273.16 - 1/(273.15+d)))-10)

        return humidex

    def comfort_safety(self):
        '''
        This is a combined interpretation using windchill, heat index,
        humidex, and the dewpoint comfort scale. It returns all of those, plus
        interpretation.
        '''
        latest_reading = self.repo.get_latest()

        humidex = self.humidex()
        heat_index = self.heat_index()
        windchill = self.windchill()
        dewpoint_comfort = self.dewpoint_comfort()
        tempc = latest_reading.tempc

        comfort_safety_value = None
        comfort_safety_method = None
        comfort_safety_str = None
        activity_safety = None

        if (tempc > 26.7):
            comfort_safety_value = heat_index
            comfort_safety_method = 'heat-index'
        elif (tempc >= 15 and tempc <= 26.7):
            # Humidex is unitless, but is often reported as
            # the degrees C the weather feels like, so we'll
            # do the same.
            comfort_safety_value = humidex
            comfort_safety_method = 'humidex'
        elif (windchill is not None):
            comfort_safety_value = windchill
            comfort_safety_method = 'windchill'
        else:
            comfort_safety_method = 'tempc'
            comfort_safety_value = tempc

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
                'windchill': windchill,
                'dewpoint_comfort': dewpoint_comfort,
                'comfort_safety_str': comfort_safety_str,
                'method': comfort_safety_method,
                'comfort_safety_value': comfort_safety_value,
                'safe_to_run': activity_safety
                }

