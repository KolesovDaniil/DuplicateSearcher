"""Flask application factory"""

from flask import Flask

from app.database import db
from app.config import AppConfig
from app.registration import register
from app.celery import celery_app, init_celery


def create_app(app_config: object = AppConfig()) -> Flask:
    """Create new application object"""

    # App creation
    app = Flask(__name__)
    app.config.from_object(app_config)

    # DB app initialization
    from app import models
    db.init_app(app)

    # Celery initialization
    init_celery(celery_app, app)

    # API registration
    register(app)

    return app
