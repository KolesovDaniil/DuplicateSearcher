from flask import Flask, Blueprint
from flask_restplus import Api

from app.namespaces import VideoDuplicateNs
from app.config import AppSettings

app = Flask(__name__)
app.config.from_object(AppSettings())
api = Api(app)
api.add_namespace(VideoDuplicateNs.ns)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
