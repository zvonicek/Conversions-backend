from flask.ext.script import Manager
from sqlalchemy import MetaData
from sqlalchemy.sql.ddl import DropConstraint

from app.app import create_app
from app.config import config, Config
from app.engine.currency import fetch_currency_rates
from app.extensions import db
from app.models import *
from app.models.Task import TaskRunQuestion

app = create_app(Config())
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""

    app.run()


@manager.command
def initdb():
    """Init/reset database."""

    db.init_app(app)

    metadata = MetaData(db.engine)
    metadata.reflect()
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            db.engine.execute(DropConstraint(fk.constraint))
    db.drop_all()
    db.create_all()

    user = User()
    task1 = Task(identifier='mass-metric', name='Mass - Metric')
    task2 = Task(identifier='mass-imperial', name='Mass - Imperial')
    task3 = Task(identifier='mass-combined', name='Mass - Combined')
    task4 = Task(identifier='length-metric', name='Length - Metric')
    task5 = Task(identifier='length-imperial', name='Length - Imperial')
    task6 = Task(identifier='length-combined', name='Length - Combined')
    task7 = Task(identifier='area-metric', name='Area - Metric')
    task8 = Task(identifier='area-imperial', name='Area - Imperial')
    task9 = Task(identifier='area-combined', name='Area - Combined')

#    taskrun = TaskRun(task=task, user=user)
#    question1 = ScaleQuestion(task_en="asd")
#    question2 = ScaleQuestion(task_en="bcc")
#    taskrunquestion1 = TaskRunQuestion(position=1, taskrun=taskrun, question=question1)
#    taskrunquestion2 = TaskRunQuestion(position=0, taskrun=taskrun, question=question2)
#    taskrunquestion3 = TaskRunQuestion(position=2, taskrun=taskrun, question=question3)
#    db.session.add_all([user, task, taskrun, question1, taskrunquestion1, taskrunquestion2, taskrunquestion3])

    db.session.add_all([
        task1,
        NumericQuestion(fromValue=5, fromUnit="m", toUnit="cm", tasks=[task1]),
        NumericQuestion(fromValue=2, fromUnit="km", toUnit="m", tasks=[task1]),
        NumericQuestion(fromValue=2, fromUnit="km", toUnit="m", tasks=[task1]),
        NumericQuestion(fromValue=8, fromUnit="m", toUnit="dm", tasks=[task1]),
        NumericQuestion(fromValue=22, fromUnit="cm", toUnit="mm", tasks=[task1]),
        NumericQuestion(fromValue=4, fromUnit="dm", toUnit="mm", tasks=[task1]),
        NumericQuestion(fromValue=5, fromUnit="km", toUnit="dm", tasks=[task1]),
    ])
    db.session.commit()


@manager.command
def currency():
    #  we need to set trigger to fetch_currency_rates
    exchange_rates = fetch_currency_rates(config)

    for currency, rate in list(exchange_rates.items()):
        print('1 EUR = {0} {1}'.format(rate, currency))


@manager.command
def convert():
    from app.engine.convert import convert

    print(convert("czk", 200, "nok"))


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()