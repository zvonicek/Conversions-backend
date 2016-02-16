from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')


@api.route("/")
def home():
    return "ahoj"


@api.route("/getTaskRun", methods=['GET'])
def get_task_run():
    return "ahoj"


@api.route("updateTaskRun", methods=['POST'])
def update_task_run():
    pass
