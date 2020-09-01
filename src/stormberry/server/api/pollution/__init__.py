from flask import jsonify, request, Blueprint
from stormberry.server.util import get_repository
import statistics


pollution_blueprint = Blueprint('pollution_blueprint', __name__)

@pollution_blueprint.route('/daily-average')
def daily_average():
    repo = get_repository()
    now = datetime.datetime.now()
    day_ago = now - datetime.timedelta(days=1)

    readings = repo.get_between(day_ago, now)

    daily = {
            'pm_2_5': statistics.mean([x.pm_2_5 for x in readings if x.pm_2_5 is not None]),
            'pm_10': statistics.mean([x.pm_10 for x in readings if x.pm_10 is not None])
            }
    return jsonify(daily)

@pollution_blueprint.route('/now')
def pollution_now():
    repo = get_repository()

    now = datetime.datetime.now()
    hour_ago = now - datetime.timedelta(hours=1)

    readings = repo.get_between(hour_ago, now)
    hourly = {
        'pm_2_5': statistics.mean([x.pm_2_5 for x in readings if x.pm_2_5 is not None]),
        'pm_10': statistics.mean([x.pm_10 for x in readings if x.pm_10 is not None])
    }

    return jsonify(hourly)
