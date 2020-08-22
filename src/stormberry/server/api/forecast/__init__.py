from flask import jsonify, request, Blueprint
import datetime
from stormberry.server.util import get_repository
from stormberry.forecast import WeatherForecaster

forecast_blueprint = Blueprint('forecast_blueprint', __name__)


@forecast_blueprint.route('/basic')
def basic_prediction():
    now = datetime.datetime.now()
    ago = now - datetime.timedelta(days=1)

    datestr = ago.strftime("%Y-%m-%d %H:%M:%S")

    repo = get_repository()
    forecaster = WeatherForecaster(repo)
    upcoming_weather = forecaster.basic_forecast()

    return jsonify(upcoming_weather)
