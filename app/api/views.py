from flask import Blueprint, jsonify

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
@api.route("/getTaskRun", methods=['GET'])
def get_task_run():
    return "ahoj"


# param id
@api.route("/updateTaskRun", methods=['POST'])
def update_task_run():
    pass
