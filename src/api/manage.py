# TODO logging
from flask import Flask, Blueprint  #, request, make_response, jsonify, abort
from src.api.settings import api
from src.api.namespaces.token import ns as search_namespace

app = Flask(__name__)

def configure_app(app):
    # TODO add configs
    pass


def init_app(app):
    configure_app(app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    # TODO add namespace for search
    api.add_namespace(search_namespace)
    # api.add_namespace(update_namespace)
    app.register_blueprint(blueprint)


init_app(app)

if __name__ == '__main__':
    app.run(debug=True)  # TODO need to change before production
