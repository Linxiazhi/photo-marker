from flask import Blueprint

imm_config = Blueprint('imm_config', __name__)

from . import views

