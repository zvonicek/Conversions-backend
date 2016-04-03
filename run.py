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

    db.session.add_all([
        Task(identifier='mass_m', name='Mass - Metric'),
        Task(identifier='mass_i', name='Mass - Imperial'),
        Task(identifier='mass_c', name='Mass - Combined'),
        Task(identifier='length_m', name='Length - Metric'),
        Task(identifier='length_i', name='Length - Imperial'),
        Task(identifier='length_c', name='Length - Combined'),
        Task(identifier='area', name='Area'),
        Task(identifier='temperature_m', name='Temperature'),
        Task(identifier='temperature_i', name='Temperature'),
        Task(identifier='temperature_c', name='Temperature'),
        Task(identifier='currency_czk', name='Currency - CZK'),
        Task(identifier='currency_eur', name='Currency - EUR'),
        Task(identifier='currency_usd', name='Currency - USD'),
    ])

    # create test data

    test_task = Task(identifier='test', name='Test')
    sortA1 = SortAnswer(value="36", unit="in", presented_pos=0)
    sortA2 = SortAnswer(value="1", unit="ft", presented_pos=1)
    sortA3 = SortAnswer(value="12", unit="m", presented_pos=2)
    sortA4 = SortAnswer(value="1", unit="km", presented_pos=3)
    closeA1 = CloseEndedAnswer(value="3", unit="yd", correct=False)
    closeA2 = CloseEndedAnswer(value="10", unit="in", correct=False)
    closeA3 = CloseEndedAnswer(value="1", unit="yd", correct=True)
    closeA4 = CloseEndedAnswer(value="1", unit="yd", correct=True)
    closeA5 = CloseEndedAnswer(value="11", unit="cm", correct=False)

    db.session.add_all([
        test_task,
        ScaleQuestion(scale_min=0, scale_max=10, from_value=6, from_unit="lb", to_unit="kg", tasks=[test_task]),
        CurrencyQuestion(from_value=300, from_unit="CZK", to_unit="EUR", tasks=[test_task]),
        NumericQuestion(from_value=5, from_unit="m", to_unit="ft", tasks=[test_task], image_name="car"),
        NumericQuestion(from_value=5, from_unit="m", to_unit="ft", tasks=[test_task]),
        sortA1,
        sortA2,
        sortA3,
        sortA4,
        SortQuestion(dimensionality="length", order="asc", answers=[sortA1, sortA2, sortA3, sortA4], tasks=[test_task]),
        closeA1,
        closeA2,
        closeA3,
        CloseEndedQuestion(question_en="bicycle", question_type="estimate_height", answers=[closeA1, closeA2, closeA3], tasks=[test_task]),
        CloseEndedQuestion(question_en="bicycle", question_type="estimate_height",
                           answers=[closeA4, closeA5], tasks=[test_task], image_name="bicycle"),
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