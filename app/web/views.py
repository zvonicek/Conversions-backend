from flask import Blueprint

web = Blueprint('web', __name__, url_prefix='/', static_folder="app/static")


@web.route('')
def index():
    return ""
