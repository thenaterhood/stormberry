from flask import Flask, jsonify, send_from_directory, request, Blueprint
import datetime
import stormberry.util
from stormberry.util import weather_list_to_dict_list
from stormberry.server.util import get_repository
import json

weather_blueprint = Blueprint('weather_blueprint', __name__)

@weather_blueprint.route('/latest-reading')
def latest_reading():
    repo = get_repository()
    latest = repo.get_latest()
    return jsonify(latest.dict)

@weather_blueprint.route('/since/<start_date>')
def weather_since(start_date):
    repo = get_repository()

    readings = repo.get_between(start_date)
    return jsonify(weather_list_to_dict_list(readings))

@weather_blueprint.route('/since/<start_date>/until/<end_date>')
def weather_between(start_date, end_date):
    repo = get_repository()

    readings = repo.get_between(start_date, end_date)
    return jsonify(weather_list_to_dict_list(readings))

@weather_blueprint.route('/past-hour')
def weather_past_hour():
    now = datetime.datetime.now()
    ago = now - datetime.timedelta(hours=1)

    repo = get_repository()
    datestr = ago.strftime("%Y-%m-%d %H:%M:%S")
    readings = repo.get_between(datestr)
    return jsonify(weather_list_to_dict_list(readings))

@weather_blueprint.route('/past-day')
def weather_past_day():
    now = datetime.datetime.now()
    ago = now - datetime.timedelta(days=1)

    repo = get_repository()
    datestr = ago.strftime("%Y-%m-%d %H:%M:%S")
    readings = repo.get_between(datestr)
    return jsonify(weather_list_to_dict_list(readings))

@weather_blueprint.route('/past-week')
def weather_past_week():
    now = datetime.datetime.now()
    ago = now - datetime.timedelta(days=7)
    repo = get_repository()
    datestr = ago.strftime("%Y-%m-%d %H:%M:%S")

    readings = repo.get_between(datestr)
    return jsonify(weather_list_to_dict_list(readings))

