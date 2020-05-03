"""Flask application factory"""

from flask import Flask

from app.database import db
from app.config import Config
from app.registration import register


def create_app(app_config: object = Config()) -> Flask:
    """Create new application object"""

    # App creation
    app = Flask(__name__)
    app.config.from_object(app_config)

    # DB app initialization
    db.init_app(app)

    # API registration
    register(app)

    return app
