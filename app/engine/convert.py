import os

import inflection
from flask import current_app
from pint import UnitRegistry, UndefinedUnitError
from app.engine import currency
from app.config import config


def register_exchange_rates(exchange_rates):
    """
    Add currency definitions with exchange rates to unit registery.
    :return:
    :rtype:
    :param exchange_rates: mapping of currencies.
    :type exchange_rates: {symbol: rate}
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

        # print('Registering currency : %r', definition)
        ureg.define(definition)


def convert(quantity_from, value_from, quantity_to):
    """
    :param quantity_from: quantity identifier (eg. 'm' for meters)
    :type quantity_from: String
    :param value_from: amount (eg. 5)
    :type value_from: Number
    :param quantity_to: output quantity identifier (eg. 'cm' for centimetres)
    :type quantity_to: String
    :return: quantity object with converted value (eg. containing 500 cm)
    :rtype: Pint.Quantity
    """

    from_q = ureg.Quantity(value_from, quantity_from)
    to_q = ureg.Quantity(1, quantity_to)
    return from_q.to(to_q)


def to_normalized(quantity_from, value_from):
    """
    Returns unit normalized in base style as implemented in Pint lib
    :param quantity_from: quantity identifier (eg. 'm' for meters)
    :type quantity_from: String
    :param value_from: amount (eg. 5)
    :type value_from: Number
    :return: normalized amount of provided unit (eg. 500 if base unit is centimeter)
    :rtype: Number
    """

    from_q = ureg.Quantity(value_from, quantity_from)
    return from_q.to_base_units().magnitude


# formatters


def format_number(number):
    """
    Format number to correct string representation (with 3 decimal places, without trailing zeros)
    :param number: nubmer (eg. 2.43356)
    :type number: Int
    :return: string representing number (eg. "2.433")
    :rtype: String
    """
    return "{0:.3f}".format(number).rstrip('0').rstrip('.')


def format_quantity_unit(unit, plural=False):
    """
    Format unit to printable string (eg. "meter")
    :param unit: unit object
    :type unit: Pint.Unit
    :param plural:
    :type plural: Boolean
    :return: formated quantity string (eg. "meter")
    :rtype: String
    """

    outputs = {"degC": "°C", "degF": "°F", "yd2": "square yard", "mi2": "square mile", "ft2": "square foot",
               "in2": "square inch", "cm2": "square centimeter", "dm2": "square decimeter", "m2": "square meter",
               "km2": "square kilometer", "fp": "football pitch", "US_ton": "US ton", "metric_ton": "metric tonne"}

    unit_string = outputs.get('{:C}'.format(unit), '{:P}'.format(unit))
    if plural and unit != "degC" and unit != "degF" and "[currency]" not in list(unit.dimensionality):
        unit_string = inflection.pluralize(unit_string)

    return unit_string


def format_unit(unit):
    """
    Format unit to printable string (eg. "meter")
    :param unit: unit identifier (eg. 'm' for meters)
    :type unit: String
    :return: formated quantity string (eg. "meter")
    :rtype: String
    """

    q = ureg.parse_units(unit)
    return format_quantity_unit(q)


def format_quantity(quantity):
    """
    Formats Pint.Quantity
    :param quantity: quantity object
    :type quantity: Pint.Quantity
    :return: formatted unit string (eg. '5 meters')
    :rtype: String
    """

    return "{0} {1}".format(format_number(quantity.magnitude), format_quantity_unit(quantity.units, quantity.magnitude > 1))


def format_value(unit_from, value_from):
    """
    Formats provided unit and value to single string
    :param unit_from: unit identifier (eg. 'm' for meters)
    :type unit_from: String
    :param value_from: amount (eg. 5)
    :type value_from: Number
    :return: formated unit string (eg. '5 meters')
    :rtype: String
    """

    return format_quantity(ureg.Quantity(value_from, unit_from))


ureg = UnitRegistry()
rates = currency.get_currency_rates(config)
register_exchange_rates(rates)
ureg.load_definitions(os.path.join(os.path.dirname(__file__), 'config/custom_units.txt'))