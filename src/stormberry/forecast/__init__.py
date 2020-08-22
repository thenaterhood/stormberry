import datetime

class WeatherForecaster:

    __slots__ = ('repo')

    def __init__(self, repo):
        self.repo = repo

    def basic_forecast(self):
        '''
        Does some magic and decides what the weather might be.
        This returns a _general_ prediction of what type
        of weather might be to come.

        This returns a bare barometer trend and interpretation
        as well as a stormberry-specific interpretation.
        '''
        now = datetime.datetime.now()
        day_ago = now - datetime.timedelta(days=1)
        three_hours_ago_delta = datetime.timedelta(hours=3)
        three_hours_ago = now - three_hours_ago_delta

        datestr = three_hours_ago.strftime("%Y-%m-%d %H:%M:%S")
        readings = self.repo.get_between(datestr)
        pressures = [x.pressure_inHg for x in readings]
        times = [x.timestamp.timestamp() for x in readings]
        mean_pressure = sum(pressures) / len(pressures) if len(pressures) > 1 else 1

        pressure_slope, pressure_intercept = self._basic_linear_regression(times, pressures)

        upcoming_weather = None
        upcoming_tempc = None

        # based on https://www.thoughtco.com/how-to-read-a-barometer-3444043
        if (mean_pressure >= 30.20):
            if (pressure_slope >= 0):
                upcoming_weather = "fair"
            elif (pressure_slope < 0 and pressure_slope > -1):
                upcoming_weather = "fair"
            elif (pressure_slope < 0 and pressure_slope < -1):
                upcoming_weather = "cloudy-and-warm"

        elif (mean_pressure > 29.75):
            if (pressure_slope >= 0):
                upcoming_weather = "more-of-the-same"
            elif (pressure_slope < 0 and pressure_slope > -1):
                upcoming_weather = "little-change"
            elif (pressure_slope < 0 and pressure_slope < -1):
                upcoming_weather = "precipitation-likely"

        elif (mean_pressure < 29.75):
            if (pressure_slope >= 0):
                upcoming_weather = "clearing-and-cool"
            elif (pressure_slope < 0 and pressure_slope > -1):
                upcoming_weather = "precipitation"
            elif (pressure_slope < 0 and pressure_slope < -1):
                upcoming_weather = "storms"

        forecast_data = {
                'prediction': upcoming_weather,
                'pressure_trend': pressure_slope,
                'hours': 24,
                'mean_pressure': mean_pressure,
                'predicted_temp': upcoming_tempc
                }

        forecast_data.update(self.trend_since(three_hours_ago_delta))
        return forecast_data

    def trend_since(self, time_delta):
        now = datetime.datetime.now()
        time_ago = now - time_delta

        time_ago_str = time_ago.strftime("%Y-%m-%d %H:%M:%S")
        readings = self.repo.get_between(time_ago_str)

        pressures = [x.pressure_inHg for x in readings]
        tempcs = [x.tempc for x in readings]
        dewpoints = [x.dewpointc for x in readings]
        times = [x.timestamp.timestamp() for x in readings]

        pressure_trend, _ = self._basic_linear_regression(times, pressures)
        temp_trend, _ = self._basic_linear_regression(times, tempcs)
        dewpoint_trend, _ = self._basic_linear_regression(times, dewpoints)

        return {
                'pressure_trend': pressure_trend,
                'tempc_trend': temp_trend,
                'dewpoint_trend': dewpoint_trend
                }

    def _basic_linear_regression(self, x, y):
        # mostly copied from http://jmduke.com/posts/basic-linear-regressions-in-python/
         # todo: either switch to numpy, or something
        length = len(x)
        sum_x = sum(x)
        sum_y = sum(y)

        # σx^2
        sum_x_squared = sum(map(lambda a: a * a, x))
        # σxy
        sum_of_products = sum([x[i] * y[i] for i in range(length)])

        a = (sum_of_products - (sum_x * sum_y) / length) / (sum_x_squared - ((sum_x ** 2) / length))
        b = (sum_y - a * sum_x) / length
        return a, b

