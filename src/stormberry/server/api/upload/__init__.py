from flask import jsonify, request, Blueprint
from datetime import datetime
import stormberry.util
from stormberry.weather_reading import WeatherReading
from stormberry.server.util import get_repository
from stormberry.config import Config


upload_blueprint = Blueprint('upload_blueprint', __name__)

@upload_blueprint.route('/', methods = [ "POST" ])
def upload_reading():
    if request.method != 'POST':
        return "Invalid method - You can only POST to this endpoint", 405
    config = Config()

    try:
        cfg_upload_token = config.get("SERVER", "UPLOAD_TOKEN")
    except:
        return jsonify({"error": "No upload token configured"}), 500

    request_token = request.form.get('token')
    if request_token == "" or request_token != cfg_upload_token:
        return jsonify({"error": "Bad token"}), 403

    try:
        reading_time = datetime.strptime(request.form.get('timestr'), "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return jsonify({"error": "invalid date"}), 400

    weather_reading = WeatherReading(
        tempc = request.form.get('tempc', type=float),
        humidity = request.form.get('humidity', type=float),
        pressureMillibars = request.form.get('pressureMillibars', type=float),
        date = reading_time,
        pressureInchesHg = request.form.get('pressureInchesHg', type=float),
        wind_mph = request.form.get('wind_mph', type=float),
        pm_2_5 = request.form.get('pm_2_5', type=float),
        pm_10 = request.form.get('pm_10', type=float),
        precipitation_cm = request.form.get('precipitation_cm', type=float),
        noise_dB = request.form.get('noise_dB', type=float),
        pressure_hectopascal = request.form.get('pressure_hectopascal', type=float),
        wet_bulb_temp_c = request.form.get('wet_bulb_temp_c', type=float),
        globe_temp_c = request.form.get('globe_temp_c', type=float)
    )

    repo = get_repository()
    repo.store_reading(weather_reading)

    return jsonify({}), 200
