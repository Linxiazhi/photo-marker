# -*-coding: utf-8-*-
from flask import Flask
from config import config
from models import db


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # TODO(Linx) import bluprint then register in app.
    from infomation import information as info_blueprint
    app.register_blueprint(info_blueprint, url_prefix='/api/v1/info')

    from resource import resource as resource_blueprint
    app.register_blueprint(resource_blueprint, url_prefix='/api/v1/resource')

    from imm_config import imm_config as config_blueprint
    app.register_blueprint(config_blueprint, url_prefix='/api/v1/config')

    db.init_app(app)
    return app

