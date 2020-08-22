from flask import jsonify, request, Blueprint
import datetime
import stormberry.util
from stormberry.util import weather_list_to_dict_list
from stormberry.server.util import get_repository
from stormberry.interpreter import WeatherInterpreter

grafana_blueprint = Blueprint('grafana_blueprint', __name__)

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

    readings = weather_list_to_dict_list(repo.get_between(req['range']['from'], req['range']['to']))
    for r in readings:
        time_obj = datetime.datetime.strptime(r['timestr'], '%Y-%m-%d %H:%M:%S')
        grafana_ts = int(time_obj.timestamp() * 1000)
        r['grafana_ts'] = grafana_ts

    if target == "Outdoor Temperature (C)":
        for r in readings:
            reply_data.append([r['tempc'], r['grafana_ts']])
    elif target == "Outdoor Temperature (F)":
        for r in readings:
            reply_data.append([stormberry.util.c_to_f(r['tempc']), r['grafana_ts']])
    elif target == "Outdoor Dewpoint (C)":
        for r in readings:
            reply_data.append([r['dewpointc'], r['grafana_ts']])
    elif target == "Outdoor Dewpoint (F)":
        for r in readings:
            reply_data.append([stormberry.util.c_to_f(r['dewpointc']), r['grafana_ts']])
    elif target == "Outdoor Humidity":
        for r in readings:
            reply_data.append([r['humidity'], r['grafana_ts']])
    elif target == "Barometer":
        for r in readings:
            reply_data.append([r['inchesHg'], r['grafana_ts']])
    elif target == "Outdoor Safety (C)":
        interpreter = WeatherInterpreter(repo)
        comfort = interpreter.comfort_safety()
        grafana_ts = int(datetime.datetime.now().timestamp() * 1000)
        reply_data = [[comfort['comfort_safety_value'], grafana_ts]]
    elif target == "Outdoor Safety (F)":
        interpreter = WeatherInterpreter(repo)
        comfort = interpreter.comfort_safety()
        grafana_ts = int(datetime.datetime.now().timestamp() * 1000)
        reply_data = [[stormberry.util.c_to_f(comfort['comfort_safety_value']), grafana_ts]]

    #if request.form['targets'][0]['target'] == "weather-week":
    #    return weather_past_week()
    return jsonify([{
            'datapoints': reply_data,
            'target': target
            }])

