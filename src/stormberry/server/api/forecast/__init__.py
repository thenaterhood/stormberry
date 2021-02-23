from flask import jsonify, request, Blueprint
import datetime
from stormberry.server.util import get_repository
from stormberry.forecast import WeatherForecaster

forecast_blueprint = Blueprint('forecast_blueprint', __name__)


@forecast_blueprint.route('/basic')
def basic_prediction():
    repo = get_repository()
    forecaster = WeatherForecaster(repo)
    upcoming_weather = forecaster.basic_forecast()

    if upcoming_weather is not None:
        return jsonify(upcoming_weather)
    else:
        return jsonify({})
