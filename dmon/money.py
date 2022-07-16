# -*- coding: utf-8 -*-
"""Classes to manipulate monetary values.
"""

import os
import json
import importlib.resources
from datetime import datetime
from decimal import Decimal as D
from enum import Enum
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
    elif on_date == _today():
        api_environment = 'MONEY_RATES_API_KEY'
        api_key = os.environ.get(api_environment, '')
        if not api_key:
            raise RuntimeError('Need an api key for https://www.exchangerate-api.com '
                               f'in the environment variable {api_environment}')

        # With their paid plans this could be
        # https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY
        url = (f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD')
        response = requests.get(url)
        data = response.json()
        with open(fname, 'w', encoding='utf-8') as fout:
            fout.write(json.dumps(data))
    else:
        raise RuntimeError('No rates for ' + on_date)

    currencies = set(item.value.upper() for item in Currency)
    return {Currency(c.lower()): r for c, r in data['conversion_rates'].items()
            if c in currencies}


class BaseMoney():
    on_date_override = None
    default_currency = Currency.EUR
    output_currency = None
    rates = None
    reverse_symbols = {v: k for k, v in CurrencySymbols.items()}

    # These can be used in several currencies, choose one:
    reverse_symbols['C$'] = Currency.CAD
    reverse_symbols['A$'] = Currency.AUD
    reverse_symbols['$'] = Currency.USD
    reverse_symbols['£'] = Currency.GBP

    def __init__(self, amount, currency=None, on=None, my_output_currency=None,
                 amount_is_cents=False):
        if isinstance(amount, tuple):
            amount, currency, on = amount
            amount_is_cents = True

        self.on_date = self.on_date_override if self.on_date_override else (on or _today())

        if currency is None:
            currency = self.default_currency

        self._amount = D(amount) if amount_is_cents else Cents * D(amount)
        self.currency = self.to_currency_enum(currency)
        self.my_output_currency = (self.to_currency_enum(my_output_currency)
                                   if my_output_currency
                                   else None)

    def to_currency_enum(self, currency):
        return Currency(self.reverse_symbols.get(currency, currency))

    def as_tuple(self):
        return self._amount, self.currency.value, self.on_date

    def in_currency(self, currency):
        if currency == self.currency:
            return self._amount

        if self.rates is None:
            self.rates = get_rates(self.on_date)

        return (self._amount * D(self.rates[self.to_currency_enum(currency)]) /
                D(self.rates[self.currency]))

    def amount(self, currency=None, rounding=False):
        currency = self.to_currency_enum(currency or self.currency)
        val = self._amount if currency == self.currency else self.in_currency(currency)
        return (D(round(val)) if rounding else val) / Cents

    def cents(self):
        return self._amount

    def to(self, currency, rounding=False):
        currency = self.to_currency_enum(currency)
        _amount = self.in_currency(currency)
        return self.__class__(round(_amount) if rounding else _amount, currency,
                              my_output_currency=currency, amount_is_cents=True)

    def __str__(self):
        currency = self.my_output_currency or self.output_currency or self.currency

        # output_currency may still be None
        currency = self.to_currency_enum(currency)

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
        return self.__class__((self._amount + o.in_currency(self.currency)) / Cents,
                              self.currency)

    def __radd__(self, o):
        return self + o

    def __sub__(self, o):
        return self.__class__((self._amount - o.in_currency(self.currency)) / Cents,
                              self.currency)

    def __rsub__(self, o):
        return -self + o

    def __mul__(self, n):
        return self.__class__(self._amount * D(n) / Cents, self.currency)

    __rmul__ = __mul__

    def __truediv__(self, n):
        if isinstance(n, BaseMoney):
            return self._amount / n.to(self.currency)._amount
        return self.__class__(self._amount / D(n) / Cents, self.currency)

    def __rtruediv__(self, n):
        if isinstance(n, BaseMoney):
            return n.to(self.currency)._amount / self._amount
        return self.__class__(D(n) / self._amount * Cents, self.currency)

    def __ne__(self, o):
        return rounded(self._amount) != rounded(o.in_currency(self.currency))

    def __eq__(self, o):
        return rounded(self._amount) == rounded(o.in_currency(self.currency))

    def __gt__(self, o):
        return rounded(self._amount) > rounded(o.in_currency(self.currency))

    def __ge__(self, o):
        return rounded(self._amount) >= rounded(o.in_currency(self.currency))

    def __lt__(self, o):
        return rounded(self._amount) < rounded(o.in_currency(self.currency))

    def __le__(self, o):
        return self._amount <= o.in_currency(self.currency)


class Money(type):
    def __new__(cls, currency=Currency.EUR, output=None, today=None, name=''):
        if today is True:
            today = _today()

        if not name:
            name = 'Money_' + (today if today else 'latest')
        x = super().__new__(cls, name, (BaseMoney,), {})
        x.on_date_override = today
        x.default_currency = currency
        x.output_currency = output
        return x

    def __init__(cls, *_, **__):
        super().__init__(cls, (BaseMoney,), {})
