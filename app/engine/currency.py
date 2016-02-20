# Copyright  (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-24
#

"""Script to update exchange rates from Yahoo! in the background."""

import csv
import os
from itertools import zip_longest
import re
import time
import requests

from app.extensions import cache

log = None


def grouper(n, iterable, fillvalue=None):
    """Return iterable that splits `iterable` into groups of size `n`.

    Args:
        n (int): Size of each group.
        iterable (iterable): The iterable to split into groups.
        fillvalue (object, optional): Value to pad short sequences with.

    Returns:
        iterator: Yields tuples of length `n` containing items
            from `iterable`.
    """

    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def load_yahoo_rates(symbols, config):
    """Return dict of exchange rates from Yahoo! Finance.

    Args:
        symbols (sequence): Abbreviations of currencies to fetch
            exchange rates for, e.g. 'USD' or 'GBP'.

    Returns:
        dict: `{symbol: rate}` mapping of exchange rates.
    """

    rates = {}
    count = len(symbols)

    parse_yahoo_response = re.compile(r'{0}(.+)=X'.format(config.REFERENCE_CURRENCY)).match

    # Build URL
    parts = []
    for symbol in symbols:
        if symbol == config.REFERENCE_CURRENCY:
            count -= 1
            continue
        parts.append('{0}{1}=X'.format(config.REFERENCE_CURRENCY, symbol))

    query = ','.join(parts)
    url = config.YAHOO_BASE_URL.format(query)

    # Fetch data
    # log.debug('Fetching {0} ...'.format(url))
    r = requests.get(url)
    r.raise_for_status()

    # Parse response
    lines = r.text.split('\n')
    ycount = 0
    for row in csv.reader(lines):
        if not row:
            continue

        name, rate = row
        m = parse_yahoo_response(name)

        if not m:  # Couldn't get symbol
            log.error('Invalid currency : {0}'.format(name))
            ycount += 1
            continue
        symbol = m.group(1)

        # Yahoo! returns 0.0 as rate for unsupported currencies
        # NOTE: This has changed. "N/A" is now returned for
        # unsupported currencies. That's handled in the script
        # that generates the currency list, however: an invalid
        # currency should never end up here.

        try:
            rate = float(rate)
        except ValueError:
            log.error('No exchange rate for : {0}'.format(name))
            continue

        if rate == 0:
            log.error('No exchange rate for : {0}'.format(name))
            ycount += 1
            continue

        rates[symbol] = rate
        ycount += 1

    assert ycount == count, 'Yahoo! returned {0} results, not {1}'.format(
        ycount, count)

    return rates


def fetch_currency_rates(config):
    """Retrieve all currency exchange rates.

    Batch currencies into requests of `SYMBOLS_PER_REQUEST` currencies each.

    Returns:
        list: List of `{abbr : n.nn}` dicts of exchange rates
            (relative to EUR).
    """

    currencies = {}
    rates = {}

    with open(os.path.join(os.path.dirname(__file__),
                           'currencies.tsv'), 'rt') as fp:
        reader = csv.reader(fp, delimiter='\t')
        for sym, name in reader:
            currencies[sym] = name

    for symbols in grouper(config.SYMBOLS_PER_REQUEST, currencies.keys()):
        symbols = [s for s in symbols if s]
        d = load_yahoo_rates(symbols, config)
        rates.update(d)

    return rates


def get_currency_rates(config):
    if cache.get("currency_rates"):
        return cache.get("currency_rates")
    else:
        rates = fetch_currency_rates(config)
        cache.set("currency_rates", rates)
        return rates
