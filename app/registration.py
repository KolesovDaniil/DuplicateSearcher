""""""

from flask import Flask, Blueprint
from flask_restplus import Api

from app.namespaces import ErrorNs, VideoDuplicateNs


def register(app: Flask) -> None:
    """"""

    blueprint = get_blueprint()
    create_api(blueprint)
    app.register_blueprint(blueprint)


def get_blueprint() -> Blueprint:
    """"""

    blueprint = Blueprint('api_bp', __name__, url_prefix='/api')
    return blueprint


def create_api(blueprint: Blueprint) -> None:
    """"""

    api = Api(blueprint,
              title='Tagger REST API',
              version='1.0',
              contact='Kolesov Daniil',
              contact_email='dakolesov@edu.hse.ru',
              description='Web Service for Text Tagging')

    api.add_namespace(VideoDuplicateNs.ns)
    api.add_namespace(ErrorNs.ns)
