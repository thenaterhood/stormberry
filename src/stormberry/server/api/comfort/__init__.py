from flask import jsonify, request, Blueprint
from stormberry.interpreter import WeatherInterpreter
from stormberry.server.util import get_repository

comfort_blueprint = Blueprint('comfort_blueprint', __name__)

@comfort_blueprint.route('/now')
def comfort_now():
    repo = get_repository()
    interpreter = WeatherInterpreter(repo)

    comfort = interpreter.comfort_safety()
    return jsonify(comfort)

