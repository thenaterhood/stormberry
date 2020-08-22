from flask import Flask, send_from_directory

from stormberry.server.api.grafana import grafana_blueprint
from stormberry.server.api.weather import weather_blueprint
from stormberry.server.api.forecast import forecast_blueprint
from stormberry.server.api.comfort import comfort_blueprint
from stormberry.server.util import get_repository
from stormberry.config import Config

get_repository() # This raises an exception if something goes wrong so we won't start the server

app = Flask(__name__, static_url_path='/assets', static_folder='/lib/stormberry/static_files/assets')
app.register_blueprint(grafana_blueprint, url_prefix="/api/grafana")
app.register_blueprint(weather_blueprint, url_prefix="/weather")
app.register_blueprint(forecast_blueprint, url_prefix="/predict")
app.register_blueprint(comfort_blueprint, url_prefix="/comfort")

@app.route('/')
def send_index():
    return send_from_directory('static', 'index.html')

def demo():
    '''
    Run the Flask development server as a demonstration.
    '''
    print('=============================================')
    print('If you are doing anything resembling production, DO NOT USE THIS.')
    print('You should properly configure a server and run the application with WSGI')
    print('=============================================')

    config = Config()
    port = None

    try:
        port = config.get("SERVER", "PORT")
    except:
        pass

    app.run(port=port, host='0.0.0.0')
