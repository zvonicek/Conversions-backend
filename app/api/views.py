from flask import Blueprint, jsonify, abort

from app.engine.generator import generate_game
from app.models import User, Task, TaskRun
from app.schemas.Task import task_schema, tasks_schema, taskrun_schema

api = Blueprint('api', __name__, url_prefix='/api')


@api.route("/")
def home():
    # tasks = Task.query.all()
    # result = tasks_schema.dump(tasks)
    # print(result)
    # return jsonify({"tasks": result.data})
    taskrun = TaskRun.query.first()
    result = taskrun_schema.dump(taskrun)
    return jsonify(result.data)


# param user
@api.route("/start/<task_name>/<user_id>", methods=['GET'])
def start(task_name, user_id):
    user = User.query.get(user_id)
    task = Task.query.filter_by(identifier=task_name).first()

    if user is None or task is None:
        abort(404)

    taskrun = generate_game(task, user)
    schema = taskrun_schema.dump(taskrun)
    return jsonify(schema.data)


# param id
@api.route("/updateTaskRun", methods=['POST'])
def update_task_run():
    pass
