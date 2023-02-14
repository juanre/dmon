# -*- coding: utf-8 -*-
"""Classes to manipulate monetary values.
"""

import os
import json
import time
import sqlite3

import importlib.resources
from datetime import datetime
from decimal import Decimal as D
from enum import Enum
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import requests

import dmon


Currency = None
CurrencySymbols = None
Cents = D('100')


def resdir():
    return os.environ.get('MONEY_RES', '.')


def rounded(v):
    return int(round(v))


def _today():
    return datetime.today().strftime('%Y-%m-%d')


def build_currency_symbols():
    global Currency
    global CurrencySymbols
    symbols_txt = importlib.resources.read_text(dmon, 'symbols.json')
    #with open(os.path.join(resdir(), 'symbols.json'), encoding='utf-8') as fin:
    symbols = json.loads(symbols_txt)
    Currency = Enum('Currency', ((name.upper(), name) for name in symbols.keys()))
    CurrencySymbols = {c: symbols[c.value] for c in Currency}

build_currency_symbols()


def get_rates(on_date):
    fname = os.path.join(resdir(), on_date + '-rates.json')
    if os.path.exists(fname):
        with open(fname, encoding='utf-8') as fin:
            data = json.load(fin)
    else:
        api_environment = 'MONEY_RATES_API_KEY'
        api_key = os.environ.get(api_environment, '')
        if not api_key:
            raise RuntimeError('Need an api key for https://www.exchangerate-api.com '
                               f'in the environment variable {api_environment}')

        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
        if on_date != _today():
            # Requires a paid plan
            # https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY
            url = (f'https://v6.exchangerate-api.com/v6/{api_key}/history/USD/' +
                   on_date.replace('-', '/'))

        response = requests.get(url)
        data = response.json()
        with open(fname, 'w', encoding='utf-8') as fout:
            fout.write(json.dumps(data))

    currencies = set(item.value.upper() for item in Currency)
    return {Currency(c.lower()): r for c, r in data['conversion_rates'].items()
            if c in currencies}


def build_rates_cache(from_date, to_date):
    print(f'Downloading rates from {from_date} to {to_date}')
    dt = date_parser.parse(from_date).date()
    to_dt = date_parser.parse(to_date).date()
    while dt <= to_dt:
        get_rates(str(dt))
        time.sleep(0.5)
        dt = (dt + relativedelta(days=1))


class BaseMoney():
    on_date = _today()
    default_currency = Currency.EUR
    output_currency = None
    rates = None
    reverse_symbols = {v: k for k, v in CurrencySymbols.items()}

    # These can be used in several currencies, choose one:
    reverse_symbols['C$'] = Currency.CAD
    reverse_symbols['A$'] = Currency.AUD
    reverse_symbols['$'] = Currency.USD
    reverse_symbols['£'] = Currency.GBP

    def __init__(self, amount, currency=None, amount_is_cents=False):
        if isinstance(amount, tuple):
            amount, currency = amount
            amount_is_cents = True

        if currency is None:
            currency = self.default_currency

        self._amount = D(amount) if amount_is_cents else Cents * D(amount)
        self.currency = self.to_currency_enum(currency)

    @classmethod
    def to_date(cls, dt):
        cls.on_date = dt

    def to_today(self):
        self.on_date = _today()

    def to_currency_enum(self, currency):
        return Currency(self.reverse_symbols.get(currency, currency))

    def as_tuple(self):
        return self._amount, self.currency.value

    def cents(self, currency=None):
        currency = self.to_currency_enum(currency or self.currency)
        if currency == self.currency:
            return self._amount

        if self.rates is None:
            self.rates = get_rates(self.on_date)

        return (self._amount * D(self.rates[self.to_currency_enum(currency)]) /
                D(self.rates[self.currency]))

    def amount(self, currency=None, rounding=False):
        val = self.cents(currency)
        return (D(round(val)) if rounding else val) / Cents

    def to(self, currency, rounding=False):
        currency = self.to_currency_enum(currency)
        _amount = self.cents(currency)
        return self.__class__(round(_amount) if rounding else _amount,
                              currency,
                              amount_is_cents=True)

    def normalized_amounts(self, o):
        """Returns the two values with which to operate, and their
        common currency.  If the two currencies are the same we do not
        need to do any conversions; if they are not, they will both be
        converted to the default currency.
        """
        if self.currency == o.currency:
            return self.cents(), o.cents(), self.currency
        return (self.cents(self.default_currency),
                o.cents(self.default_currency),
                self.default_currency)

    def __str__(self):
        # output_currency may still be None
        currency = self.to_currency_enum(self.output_currency or self.currency)
        # pylint: disable=bad-string-format-type
        return '%s%.2f' % (CurrencySymbols[currency], self.amount(currency, rounding=True))

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return self.__class__(-self._amount / Cents, self.currency)

    def __add__(self, o):
        # This enables expressions like sum(Eur(i) for i in range(10))
        if not isinstance(o, BaseMoney):
            o = self.__class__(D(o), self.currency)

        v1, v2, out_currency = self.normalized_amounts(o)
        return self.__class__(v1 + v2, out_currency, amount_is_cents=True)

    def __radd__(self, o):
        return self + o

    def __sub__(self, o):
        v1, v2, out_currency = self.normalized_amounts(o)
        return self.__class__(v1 - v2, out_currency, amount_is_cents=True)

    def __rsub__(self, o):
        return -self + o

    def __mul__(self, n):
        return self.__class__(self._amount * D(n), self.currency, amount_is_cents=True)

    __rmul__ = __mul__

    def __truediv__(self, n):
        if isinstance(n, BaseMoney):
            return self._amount / n.to(self.currency).cents()
        return self.__class__(self._amount / D(n), self.currency, amount_is_cents=True)

    def __ne__(self, o):
        return rounded(self._amount) != rounded(o.cents(self.currency))

    def __eq__(self, o):
        return rounded(self._amount) == rounded(o.cents(self.currency))

    def __gt__(self, o):
        return rounded(self._amount) > rounded(o.cents(self.currency))

    def __ge__(self, o):
        return rounded(self._amount) >= rounded(o.cents(self.currency))

    def __lt__(self, o):
        return rounded(self._amount) < rounded(o.cents(self.currency))

    def __le__(self, o):
        return self._amount <= o.cents(self.currency)

    def __conform__(self, protocol):
        """Enables writing to an sqlite database

        https://docs.python.org/3/library/sqlite3.html#how-to-write-adaptable-objects

        Will also need the inverse (string to Money_*) to be registered with
        register_converter.
        """
        if protocol is sqlite3.PrepareProtocol:
            amount, currency = self.as_tuple()
            return f"{str(amount)};{currency}"
        return None


class Money(type):
    def __new__(cls, currency=Currency.EUR, output=None, on=None, name=''):
        if not name:
            name = 'Money_' + (on if on else 'latest')
        x = super().__new__(cls, name, (BaseMoney,), {})
        x.on_date = on or _today()
        x.default_currency = currency
        x.output_currency = output
        return x

    def __init__(cls, *_, **__):
        super().__init__(cls, (BaseMoney,), {})


def add_args(parser):
    parser.add_argument('--rates-cache',
                        help=('Download the conversion rates.  It has the form of a date, '
                              'like 2022-04-34, or two.  If only one download until today, '
                              'otherwise from the first until the second, included.'),
                        type=str,
                        nargs='+',
                        required=False)


def main(args):
    if args.rates_cache:
        from_dt = args.rates_cache[0]
        to_dt = _today() if len(args.rates_cache) == 1 else args.rates_cache[1]
        build_rates_cache(from_dt, to_dt)
