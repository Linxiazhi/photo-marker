#!/usr/bin/python
# -*-coding:utf8-*-
from app import create_app, db, models
from flask_script import Manager, Server, Shell
from flask_migrate import Migrate, MigrateCommand
from app.util.custom_error import CustomFlaskErr
from flask import jsonify
from flask_cors import CORS
import os
import logging

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)

# 自定义错误返回
@app.errorhandler(CustomFlaskErr)
def handle_flask_error(error):
    response = jsonify(error.to_dict())

    response.status_code = error.status_code

    return response


@app.errorhandler(500)
def internal_server_error(error):
    logging.error('InternalError: %s' % str(error))
    return jsonify({'Code': 'InternalError', 'Message': 'The request has been failed due to some unknown error.'}), 500


def make_shell_context():
    return dict(app=app,
                db=db,
                Info=models.Information,
                )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command("server", Server(host='0.0.0.0', port=8089))

if __name__ == '__main__':
    manager.run()


