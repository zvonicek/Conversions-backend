from flask.ext.script import Manager

from app.app import create_app
from app.extensions import db
from app.models import *
from app.models.Task import TaskRunQuestion

app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""

    app.run()


@manager.command
def initdb():
    """Init/reset database."""

    db.init_app(app)
    db.drop_all()
    db.create_all()

    user = User()
    task = Task(identifier='mass-metric', name='Mass Metric')
    taskrun = TaskRun(task=task, user=user)
    question1 = ScaleQuestion(task_en="asd")
    question2 = ScaleQuestion(task_en="bcc")
    question3 = NumericQuestion(imagePath="blabla")
    taskrunquestion1 = TaskRunQuestion(position=1, taskrun=taskrun, question=question1)
    taskrunquestion2 = TaskRunQuestion(position=0, taskrun=taskrun, question=question2)
    taskrunquestion3 = TaskRunQuestion(position=2, taskrun=taskrun, question=question3)


    db.session.add_all([user, task, taskrun, question1, taskrunquestion1, taskrunquestion2, taskrunquestion3])
    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()