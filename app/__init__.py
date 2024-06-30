from flask.app import Flask
from .config import Config
from .advanced import advanced
from .settings import settings
from flask_bootstrap import Bootstrap

def create_app():
  """App implementation
  'Constructor' of the flask app type object and its initialization.

  Returns:
      app: flask server instance
  """
  app = Flask(__name__)
  app.config.from_object(Config)
  bootstrap = Bootstrap(app)
  app.register_blueprint(advanced)
  app.register_blueprint(settings)

  return app
