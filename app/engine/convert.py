from flask import current_app
from pint import UnitRegistry, UndefinedUnitError
from app.engine import currency
from app.config import config


def register_exchange_rates(exchange_rates):
    """Add currency definitions with exchange rates to unit registery.

    Args:
        exchange_rates (dict): `{symbol: rate}` mapping of currencies.
    """
    currency_names = {}

    # EUR will be the baseline currency. All exchange rates are
    # defined relative to the euro
    #ureg.define('Euro = [currency] = eur = EUR')
    ureg.define('EUR = [currency] = eur')

    for abbr, rate in exchange_rates.items():
        #definition = '{0} = eur / {1} = {2}'.format(name, rate, abbr)
        definition = '{0} = eur / {1}'.format(abbr, rate)

        try:
            ureg.Quantity(1, abbr)
        except UndefinedUnitError:
            pass  # Unit does not exist
        else:
            print('Skipping currency %s : Unit is already defined', abbr)
            continue

        try:
            ureg.Quantity(1, abbr.lower())
        except UndefinedUnitError:
            definition += ' = {0}'.format(abbr.lower())

        print('Registering currency : %r', definition)
        ureg.define(definition)


def convert(quantity_from, value_from, value_to):
    from_q = ureg.Quantity(value_from, quantity_from)
    to_q = ureg.Quantity(1, value_to)
    return from_q.to(to_q)


ureg = UnitRegistry()
rates = currency.get_currency_rates(config)
register_exchange_rates(rates)