from flask import jsonify, request, Blueprint
import datetime
import stormberry.util
from stormberry.util import weather_list_to_dict_list
from stormberry.server.util import get_repository
from stormberry.interpreter import WeatherInterpreter

grafana_blueprint = Blueprint('grafana_blueprint', __name__)

def transform_readings_to_series(readings, fields=None):
    if len(readings) < 1:
        return {}

    transformed = {}
    for r in readings:
        grafana_ts = int(r.dict['datetime'].timestamp()*1000)

        for k in r.dict.keys():
            if fields is not None and k not in fields:
                continue

            if k not in transformed:
                transformed[k] = []

            transformed[k].append([r.dict[k], grafana_ts])

    return transformed

@grafana_blueprint.route('/')
def grafana_health():
    return jsonify({})

@grafana_blueprint.route('/search', methods = ['POST'])
def grafana_search():
    return jsonify([
        "Outdoor Temperature (C)",
        "Outdoor Temperature (F)",
        "Outdoor Dewpoint (C)",
        "Outdoor Dewpoint (F)",
        "Outdoor Humidity",
        "Barometer",
        "Outdoor Safety (C)",
        "Outdoor Safety (F)"
        ])

@grafana_blueprint.route('/query', methods = ['POST'])
def grafana_query():
    req = request.get_json()
    repo = get_repository()
    target = req['targets'][0]['target']

    reply_data = []

    weather_readings = repo.get_between(req['range']['from'], req['range']['to'])
    readings = transform_readings_to_series(weather_readings)
    interpreter = WeatherInterpreter(repo)
    comfort = interpreter.comfort_safety()
    now_grafana_ts = int(datetime.datetime.now().timestamp() * 1000)

    for target_req in req['targets']:
        target = target_req['target']

        if target == "Outdoor Temperature (C)":
            reply_data.append({
                "target": target,
                "datapoints": readings['tempc']
            })
        elif target == "Outdoor Temperature (F)":
            reply_data.append({
                "target": target,
                "datapoints": readings['tempf']
            })
        elif target == "Outdoor Dewpoint (C)":
            reply_data.append({
                "target": target,
                "datapoints": readings['dewpointc']
            })
        elif target == "Outdoor Dewpoint (F)":
            reply_data.append({
                "target": target,
                "datapoints": readings['dewpointf']
            })
        elif target == "Outdoor Humidity":
            reply_data.append({
                "target": target,
                "datapoints": readings['humidity']
            })
        elif target == "Barometer":
            reply_data.append({
                "target": target,
                "datapoints": readings['inchesHg']
            })
        elif target == "Outdoor Safety (C)":
            reply_data.append({
                "target": target,
                "datapoints": [[comfort['comfort_safety_value'], now_grafana_ts]]
            })
        elif target == "Outdoor Safety (F)":
            reply_data.append({
                "target": target,
                "datapoints": [[stormberry.util.c_to_f(comfort['comfort_safety_value']), now_grafana_ts]]
            })

    return jsonify(reply_data)

