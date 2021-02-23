from flask import jsonify, request, Blueprint
from stormberry.server.util import get_repository
import datetime
import statistics


pollution_blueprint = Blueprint('pollution_blueprint', __name__)

@pollution_blueprint.route('/daily-average')
def daily_average():
    now = datetime.datetime.now()
    day_ago = now - datetime.timedelta(days=1)

    return jsonify(get_quality_between(day_ago, now))

@pollution_blueprint.route('/now')
def pollution_now():
    repo = get_repository()

    now = datetime.datetime.now()
    hour_ago = now - datetime.timedelta(hours=1)

    return jsonify(get_quality_between(hour_ago, now))

def get_quality_between(start, end):

    repo = get_repository()

    readings = repo.get_between(start, end)

    daily = {
        'pm_2_5': None,
        'pm_10': None,
        'aqi_category': None,
        'aqi': None
    }

    if len(readings) < 1:
        return daily

    pm_2_5_values = [x.pm_2_5 for x in readings if x.pm_2_5 is not None]
    pm_10_values = [x.pm_10 for x in readings if x.pm_10 is not None]

    if len(pm_10_values) < 1 or len(pm_2_5_values) < 1:
        return daily

    # The following numbers and formulas come from the U.S. EPA:
    # https://www.epa.gov/sites/production/files/2014-05/documents/zell-aqi.pdf
    pm_2_5_mean = statistics.mean(pm_2_5_values)
    pm_2_5_min = min(pm_2_5_values)
    pm_2_5_max = max(pm_2_5_values)

    pm_2_5_aqi_min = 0
    pm_2_5_aqi_max = 50

    if pm_2_5_mean > 15.5 and pm_2_5_mean <= 40.4:
        pm_2_5_aqi_min = 51
        pm_2_5_aqi_max = 100
    elif pm_2_5_mean > 40.4 and pm_2_5_mean <= 65.4:
        pm_2_5_aqi_min = 101
        pm_2_5_aqi_max = 150
    elif pm_2_5_mean > 65.4 and pm_2_5_mean <= 150.4:
        pm_2_5_aqi_min = 151
        pm_2_5_aqi_max = 200
    elif pm_2_5_mean > 150.4 and pm_2_5_mean <= 250.4:
        pm_2_5_aqi_min = 201
        pm_2_5_aqi_max = 300
    elif pm_2_5_mean > 250.4:
        pm_2_5_aqi_min = 301
        pm_2_5_aqi_max = 500

    pm_10_mean = statistics.mean(pm_10_values)
    pm_10_min = min(pm_10_values)
    pm_10_max = max(pm_10_values)

    pm_10_aqi_min = 0
    pm_10_aqi_max = 50

    if pm_10_mean > 54 and pm_10_mean <= 154:
        pm_10_aqi_min = 51
        pm_10_aqi_max = 100
    elif pm_10_mean > 154 and pm_10_mean <= 254:
        pm_10_aqi_min = 101
        pm_10_aqi_max = 150
    elif pm_10_mean > 254 and pm_10_mean <= 354:
        pm_10_aqi_min = 151
        pm_10_aqi_max = 200
    elif pm_10_mean > 354 and pm_10_mean <= 424:
        pm_10_aqi_min = 201
        pm_10_aqi_max = 300
    elif pm_10_mean > 424:
        pm_10_aqi_min = 301
        pm_10_aqi_max = 500

    aqi_pm_2_5 = ((pm_2_5_mean - pm_2_5_min) * (pm_2_5_max - pm_2_5_min)) / (pm_2_5_max - pm_2_5_min)
    aqi_pm_2_5 = aqi_pm_2_5 + pm_2_5_aqi_min

    aqi_pm_10 = ((pm_10_mean - pm_10_min) * (pm_10_max - pm_10_min)) / (pm_10_max - pm_10_min)
    aqi_pm_10 = aqi_pm_10 + pm_10_aqi_min

    aqi = max(aqi_pm_2_5, aqi_pm_10)

    aqi_category = "good"
    if aqi > 50 and aqi <= 100:
        aqi_category = "moderate"
    elif aqi > 100 and aqi <= 150:
        aqi_category = "unhealthy-for-sensitive-groups"
    elif aqi > 150 and aqi <= 200:
        aqi_category = "unhealthy"
    elif aqi > 200 and aqi <= 300:
        aqi_category = "very-unhealthy"
    elif aqi > 300:
        aqi_category = "hazardous"

    daily = {
            'pm_2_5': statistics.mean([x.pm_2_5 for x in readings if x.pm_2_5 is not None]),
            'pm_10': statistics.mean([x.pm_10 for x in readings if x.pm_10 is not None]),
            'aqi': aqi,
            'aqi_category': aqi_category
            }

    return daily
