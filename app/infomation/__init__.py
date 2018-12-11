from flask import Blueprint

information = Blueprint('info', __name__)

from . import views

