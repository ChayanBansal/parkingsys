import os
from flask import Flask
from logging.config import dictConfig


def create_app(test_config=None) -> Flask:
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    app=Flask(__name__, instance_relative_config=True)
    from flask_cors import CORS
    CORS(app)
    app.config.from_object("parkingsys.default_config.Config")
    app.config.from_mapping({
        "DOC_DB_PATH": os.path.join(app.root_path, 'db.json'),
        "RELATIONAL_DB_PATH": os.path.join(app.root_path, 'parkingsys.db')
        })

    if test_config is not None:
        app.config.from_mapping(test_config)
        
    from parkingsys import db
    db.init_app(app)
    
    @app.route("/", methods=["GET", "POST"])
    def index():
        return "App is up and running!"

    from parkingsys.v1 import api_bp as v1_bp
    app.register_blueprint(v1_bp)

    return app