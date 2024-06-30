from flask import Blueprint

advanced = Blueprint('advanced', __name__, url_prefix='/advanced')

from . import views