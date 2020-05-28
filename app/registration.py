""""""

from flask import Flask, Blueprint
from flask_restplus import Api

from app.namespaces import ErrorNs, FoldersNs, TaskNs


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
              title='VideoDuplicateRecognizer REST API',
              version='1.0',
              contact='Dina Khasanova',
              contact_email='dfkhasanova@edu.hse.ru',
              description='Web Service for Video Duplicate Recognition')

    api.add_namespace(FoldersNs.ns)
    api.add_namespace(TaskNs.ns)
    api.add_namespace(ErrorNs.ns)
