from flask import Blueprint, jsonify, abort, request

from app.engine.generator import generate_game
from app.extensions import db
from app.models import User, Task, TaskRun
from app.models.Task import TaskRunQuestion
from app.serialization.Task import task_schema, tasks_schema, taskrun_schema

api = Blueprint('api', __name__, url_prefix='/api')


# param user
@api.route("/start", methods=['GET'])
def start():
    global user
    user = User.query.filter_by(uuid=request.args.get('user')).first()
    if user is None:
        user = User(uuid=request.args.get('user'))
        db.session.add(user)

    user.app_version = request.args.get('version')
    user.language = request.args.get('language')
    db.session.commit()

    task = Task.query.filter_by(identifier=request.args.get('task')).first()

    if task is None:
        abort(404)

    taskrun = generate_game(task, user)
    schema = taskrun_schema.dump(taskrun)
    return jsonify(schema.data)


# param id
@api.route("/updateTaskRun", methods=['POST'])
def update_task_run():
    data = request.json

    db.session.query(TaskRun).filter(TaskRun.id == data["id"]).update({"completed": not data["aborted"]})

    for question in data["questions"]:
        db.session.query(TaskRunQuestion).filter(TaskRunQuestion.taskrun_id == data["id"])\
            .filter(TaskRunQuestion.question_id == question["id"]) \
            .update({"correct": question["correct"], "time": question["time"], "hint_shown": question["hintShown"],
                     "answer": question["answer"]})

    db.session.commit()

    return ""
