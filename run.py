from flask.ext.script import Manager
from sqlalchemy import MetaData
from sqlalchemy.sql.ddl import DropConstraint

from app.app import create_app
from app.config import config, Config
from app.engine.currency import fetch_currency_rates
from app.extensions import db
from app.models import *
from app.models.Task import TaskRunQuestion

app = create_app(config)
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

    task1 = Task(identifier='mass-metric', name='Mass - Metric')
    task2 = Task(identifier='mass-imperial', name='Mass - Imperial')
    task3 = Task(identifier='mass-combined', name='Mass - Combined')
    task4 = Task(identifier='length-metric', name='Length - Metric')
    task5 = Task(identifier='length-imperial', name='Length - Imperial')
    task6 = Task(identifier='length-combined', name='Length - Combined')
    task7 = Task(identifier='area-metric', name='Area - Metric')
    task8 = Task(identifier='area-imperial', name='Area - Imperial')
    task9 = Task(identifier='area-combined', name='Area - Combined')

#    taskrun = TaskRun(task=t-ask, user=user)
#    question1 = ScaleQuestion(task_en="asd")
#    question2 = ScaleQuestion(task_en="bcc")
#    taskrunquestion1 = TaskRunQuestion(position=1, taskrun=taskrun, question=question1)
#    taskrunquestion2 = TaskRunQuestion(position=0, taskrun=taskrun, question=question2)
#    taskrunquestion3 = TaskRunQuestion(position=2, taskrun=taskrun, question=question3)
#    db.session.add_all([user, task, taskrun, question1, taskrunquestion1, taskrunquestion2, taskrunquestion3])

    sortA1 = SortAnswer(value="100", unit="cm", presented_pos=0)
    sortA2 = SortAnswer(value="200", unit="dm", presented_pos=1)
    sortA3 = SortAnswer(value="2", unit="m", presented_pos=2)
    sortA4 = SortAnswer(value="3500", unit="mm", presented_pos=3)
    sortA5 = SortAnswer(value="9", unit="dm", presented_pos=4)

    closeA1 = CloseEndedAnswer(value="15", unit="dm", correct=False)
    closeA2 = CloseEndedAnswer(value="15", unit="m", correct=False)
    closeA3 = CloseEndedAnswer(value="15", unit="cm", correct=True)

    db.session.add_all([
        task1,
        NumericQuestion(from_value=5, from_unit="m", to_unit="cm", tasks=[task1]),
        NumericQuestion(from_value=2, from_unit="km", to_unit="m", tasks=[task1]),
        NumericQuestion(from_value=8, from_unit="m", to_unit="dm", tasks=[task1]),
        NumericQuestion(from_value=22, from_unit="cm", to_unit="mm", tasks=[task1]),
        NumericQuestion(from_value=4, from_unit="dm", to_unit="mm", tasks=[task1]),
        NumericQuestion(from_value=5, from_unit="km", to_unit="dm", tasks=[task1]),
        ScaleQuestion(scale_min=20, scale_max=100, from_value=50000, from_unit="m", to_unit="km", tasks=[task1]),
        sortA1,
        sortA2,
        sortA3,
        sortA4,
        sortA5,
        SortQuestion(dimensionality="length", order="asc", answers=[sortA1, sortA2, sortA3, sortA4, sortA5], tasks=[task1]),
        closeA1,
        closeA2,
        closeA3,
        CloseEndedQuestion(question_en="What's better estimate for the length of a mobile phone", answers=[closeA1, closeA2, closeA3], tasks=[task1],),
        CurrencyQuestion(from_value=300, from_unit="CZK", to_unit="EUR", tasks=[task1]),
        CurrencyQuestion(from_value=80, from_unit="NOK", to_unit="CZK", tasks=[task1])
    ])
    db.session.commit()


@manager.command
def currency():
    #  we need to set trigger to fetch_currency_rates
    exchange_rates = fetch_currency_rates(config)

    for currency, rate in list(exchange_rates.items()):
        print('1 EUR = {0} {1}'.format(rate, currency))


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()