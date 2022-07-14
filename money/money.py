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

import money


Currency = None
CurrencySymbols = None
Cents = D('100')


def resdir():
    return os.environ.get('MONEY_RES', '.')


def build_currency_symbols():
    global Currency
    global CurrencySymbols
    symbols_txt = importlib.resources.read_text(money, 'symbols.json')
    #with open(os.path.join(resdir(), 'symbols.json'), encoding='utf-8') as fin:
    symbols = json.loads(symbols_txt)
    Currency = Enum('Currency', ((name.upper(), name) for name in symbols.keys()))
    CurrencySymbols = {c: symbols[c.value] for c in Currency}

build_currency_symbols()


def get_rates(on_date=None):
    fname = os.path.join(resdir(),
                         (on_date if on_date else
                          datetime.today().strftime('%Y-%m-%d')) + '-rates.json')
    if os.path.exists(fname):
        with open(fname, encoding='utf-8') as fin:
            print('reading ' + fname)
            data = json.load(fin)
    elif on_date is None:
        api_environment = 'MONEY_RATES_API_KEY'
        api_key = os.environ.get(api_environment, '')
        if not api_key:
            raise RuntimeError('Need an api key for https://www.exchangerate-api.com '
                               f'in the environment variable {api_environment}')
        url = (f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD')
        response = requests.get(url)
        data = response.json()
        print('saving ' + fname)
        with open(fname, 'w', encoding='utf-8') as fout:
            fout.write(json.dumps(data))
    else:
        raise RuntimeError('No rates for ' + on_date)

    currencies = set(item.value.upper() for item in Currency)
    return {Currency(c.lower()): r for c, r in data['conversion_rates'].items()
            if c in currencies}


class BaseMoney():
    on_date = None
    default_currency = Currency.EUR
    output_currency = None
    rates = None
    reverse_symbols = {v: k for k, v in CurrencySymbols.items()}

    # These can be used in several currencies, choose one:
    reverse_symbols['C$'] = Currency.CAD
    reverse_symbols['A$'] = Currency.AUD
    reverse_symbols['$'] = Currency.USD
    reverse_symbols['£'] = Currency.GBP

    def __init__(self, amount, currency=None, my_output_currency=None, amount_is_cents=False):
        if currency is None:
            currency = self.default_currency
        self._amount = D(amount if amount_is_cents else int(round(int(Cents) * D(amount))))
        self.currency = self.to_currency_enum(currency)
        self.my_output_currency = (self.to_currency_enum(my_output_currency)
                                   if my_output_currency
                                   else None)

    def to_currency_enum(self, currency):
        return Currency(self.reverse_symbols.get(currency, currency))

    def in_currency(self, currency):
        if currency == self.currency:
            return self._amount

        if self.rates is None:
            self.rates = get_rates(self.on_date)

        return (self._amount *
                D(self.rates[self.to_currency_enum(currency)] /
                  self.rates[self.currency]))

    def as_tuple(self):
        return self._amount, self.currency.value

    def amount(self, currency=None):
        currency = self.to_currency_enum(currency or self.currency)
        return D(round(self._amount if (currency == self.currency)
                       else self.in_currency(currency)) / Cents)

    def cents(self):
        return self._amount

    def to(self, currency, rounding=False):
        currency = self.to_currency_enum(currency)
        _amount = self.in_currency(currency) / Cents
        return self.__class__(int(round(_amount)) if rounding else _amount,
                              currency, my_output_currency=currency)

    def __str__(self):
        currency = self.my_output_currency or self.output_currency or self.currency

        # output_currency may still be None
        currency = self.to_currency_enum(currency)

        # pylint: disable=bad-string-format-type
        return '%s%.2f' % (CurrencySymbols[currency], self.amount(currency))

    def __repr__(self):
        return str(self)

    def __add__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self.__class__((self._amount + o.in_currency(self.currency)) / Cents,
                              self.currency)

    def __sub__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self.__class__((self._amount - o.in_currency(self.currency)) / Cents,
                              self.currency)

    def __mul__(self, n):
        return self.__class__(self._amount * D(n) / Cents, self.currency)

    __rmul__ = __mul__

    def __truediv__(self, n):
        return self.__class__(self._amount / D(n) / Cents, self.currency)

    def __ne__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self._amount != o.in_currency(self.currency)

    def __eq__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self._amount == o.in_currency(self.currency)

    def __gt__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self._amount > o.in_currency(self.currency)

    def __ge__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self._amount >= o.in_currency(self.currency)

    def __lt__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self._amount < o.in_currency(self.currency)

    def __le__(self, o):
        if not isinstance(o, BaseMoney):
            # Assume it's a number
            o = self.__class__(D(o), self.currency)
        return self._amount <= o.in_currency(self.currency)


class Money(type):
    def __new__(cls, currency=Currency.EUR, output=None, on=None, name=''):
        if not name:
            name = 'Money_' + (on if on else 'latest')
        x = super().__new__(cls, name, (BaseMoney,), {})
        x.on_date = on
        x.default_currency = currency
        x.output_currency = output
        return x

    def __init__(cls, *_, **__):
        super().__init__(cls, (BaseMoney,), {})


class TupleMoney(BaseMoney):
    def __init__(self, tpl):
        amount, currency = tpl
        self._amount = D(amount)
        self.currency = self.to_currency_enum(currency)
        self.my_output_currency = self.to_currency_enum(currency)



def _try():
    M = Money()
    print(M.on_date)
    print(M(23))
    print(M(40).in_currency('usd'))
    print(M(40).amount(Currency.USD))
    print(M(40).amount())
    print(M(40))
    print(M(50, 'eur').to(Currency.GBP))

    # Din = Money(on='2021-10-16')
    # print(Din.on_date)
    # print(Din(40).in_currency(Currency.USD))
    # print(Din(50).in_currency(Currency.GBP))
    #
    # print(Din(10, Currency.EUR) + Din(20, Currency.EUR))
    # print(Din(10, Currency.EUR) + Din(20, Currency.USD))
    # print((Din(10, Currency.EUR) + Din(20, Currency.USD)).to(Currency.GBP))
    #
    # print((Din(10, Currency.EUR) + Din(20, Currency.USD)).to(Currency.GBP) * 10)
    # print(10 * (Din(10, Currency.EUR) + Din(20, Currency.USD)).to(Currency.GBP))
    # print((10 * (Din(10) + Din(20, Currency.USD)).to(Currency.GBP)).to(Currency.EUR))
    #
    # print((10 * (Din(10) + M(20, Currency.USD)).to(Currency.GBP)).to(Currency.EUR))
    #
    # Din = Money(Currency.GBP)
    # print(Din(10, Currency.EUR) + Din(10))
    #
    # Din = Money('£', output='C$')
    # print(Din(10, '€') + Din(10))
    #
    # C = Money('£', '$')
    # print(Din(10, '€') + C(10))
    # print(C(10, '€') + Din(10) + C(10))
    #
    # F = Money('£')
    # print(Din(10, 'A$') + F(10) + F(10))
    # print(F(10, 'A$') + Din(10) + C(10))
    #
    # print((F(10, 'A$') + Din(10) + C(10)).to(Currency.MXN))
    # print(F(20) + 39)
    #
    # print(Eur(10, Currency.EUR))
    # print(Eur(10, Currency.USD))
    #
    # print(Eur(10) + 10)
    #
    # print(Eur(10) == Eur(10))
    # print(Eur(10) != Eur(10))
    # print(Eur(10) < Eur(20))
    # print(Eur(10) <= Eur(20))
    # print(Eur(10) <= Eur(10))
    # print(Eur(20) > Eur(10))
    # print(Eur(20) >= Eur(20))
    # print(Eur(25) >= Eur(20))
    # print(Eur(20) > Eur(20))

    a = M(30, 'eur')
    t = a.as_tuple()
    b = TupleMoney(t)
    assert a == b
    print(a, b)


if __name__ == '__main__':
    _try()
