from flask.ext.script import Manager
from sqlalchemy import MetaData
from sqlalchemy.sql.ddl import DropConstraint

from app.app import create_app
from app.config import config
from app.engine.currency import fetch_currency_rates
from app.extensions import db
from app.models import *

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

    # create tasks

    task1 = Task(identifier='mass_m', name='Mass - Metric')
    task2 = Task(identifier='mass_i', name='Mass - Im.perial')
    task3 = Task(identifier='mass_c', name='Mass - Combined')
    task4 = Task(identifier='length_m', name='Length - Metric')
    task5 = Task(identifier='length_i', name='Length - Imperial')
    task6 = Task(identifier='length_c', name='Length - Combined')
    task7 = Task(identifier='area_m', name='Area - Metric')
    task8 = Task(identifier='area_i', name='Area - Imperial')
    task9 = Task(identifier='area_c', name='Area - Combined')

    db.session.add_all([
        task1,
        task2,
        task3,
        task4,
        task5,
        task6,
        task7,
        task8,
        task9
    ])

    # create test data

    test_task = Task(identifier='test', name='Test')
    sortA1 = SortAnswer(value="100", unit="cm", presented_pos=0)
    sortA2 = SortAnswer(value="200", unit="dm", presented_pos=1)
    sortA3 = SortAnswer(value="2", unit="m", presented_pos=2)
    sortA4 = SortAnswer(value="3500", unit="mm", presented_pos=3)
    closeA1 = CloseEndedAnswer(value="15", unit="dm", correct=False)
    closeA2 = CloseEndedAnswer(value="15", unit="m", correct=False)
    closeA3 = CloseEndedAnswer(value="15", unit="cm", correct=True)
    closeA4 = CloseEndedAnswer(value="15", unit="m", correct=False)
    closeA5 = CloseEndedAnswer(value="15", unit="cm", correct=True)

    db.session.add_all([
        test_task,
        NumericQuestion(from_value=5, from_unit="m", to_unit="cm", tasks=[test_task], image_name="car"),
        NumericQuestion(from_value=5, from_unit="m", to_unit="cm", tasks=[test_task]),
        sortA1,
        sortA2,
        sortA3,
        sortA4,
        SortQuestion(dimensionality="length", order="asc", answers=[sortA1, sortA2, sortA3, sortA4], tasks=[test_task]),
        closeA1,
        closeA2,
        closeA3,
        CloseEndedQuestion(question_en="What's better estimate for the length of a mobile phone", answers=[closeA1, closeA2, closeA3], tasks=[test_task]),
        CloseEndedQuestion(question_en="What's better estimate for the length of a mobile phone",
                           answers=[closeA4, closeA5], tasks=[test_task], image_name="car"),
        CurrencyQuestion(from_value=300, from_unit="CZK", to_unit="EUR", tasks=[test_task]),
        ScaleQuestion(scale_min=0, scale_max=4000, from_value=1, from_unit="mi", to_unit="yd", tasks=[test_task]),
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