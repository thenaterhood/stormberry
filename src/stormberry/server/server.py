from flask import Flask, send_from_directory
from flask.logging import default_handler
from flask_cors import CORS

from stormberry.server.api.grafana import grafana_blueprint
from stormberry.server.api.weather import weather_blueprint
from stormberry.server.api.forecast import forecast_blueprint
from stormberry.server.api.comfort import comfort_blueprint
from stormberry.server.api.pollution import pollution_blueprint
from stormberry.server.api.upload import upload_blueprint
from stormberry.server.util import get_repository
from stormberry.config import Config
import stormberry.logging

get_repository() # This raises an exception if something goes wrong so we won't start the server

app = Flask(__name__, static_url_path='/assets', static_folder='/lib/stormberry/static_files/assets')
app.register_blueprint(grafana_blueprint, url_prefix="/api/grafana")
app.register_blueprint(weather_blueprint, url_prefix="/weather")
app.register_blueprint(forecast_blueprint, url_prefix="/predict")
app.register_blueprint(comfort_blueprint, url_prefix="/comfort")
app.register_blueprint(pollution_blueprint, url_prefix="/api/pollution")

@app.route('/')
def send_index():
    return send_from_directory('/lib/stormberry/static_files', 'index.html')

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
        enable_uploads = config.get("SERVER", "ENABLE_UPLOADS")
        upload_token = config.get("SERVER", "UPLOAD_TOKEN")
    except:
        enable_uploads = False
        upload_token = ""

    try:
        port = config.get("SERVER", "PORT")
    except:
        pass

    try:
        logdir = config.get("GENERAL", "LOGDIR")
    except:
        logdir = "/tmp"

    filehandler, termhandler = stormberry.logging.setup_handlers(logdir, "stormberry-server.log")
    stormberry.logging.setup_logging(config, "stormberry-server", [filehandler, termhandler], app.logger)
    stormberry.logging.setup_logging(config, "werkzeug", [filehandler, termhandler])

    if enable_uploads:
        app.register_blueprint(upload_blueprint, url_prefix="/api/upload")

    app.logger.removeHandler(default_handler)
    app.logger.info("Starting stormberry-server")

    repository = get_repository()
    app.logger.info("Using storage plugin %s" % repository.__class__.__name__)
    CORS(app)
    app.run(port=port, host='0.0.0.0')
