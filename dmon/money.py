# -*- coding: utf-8 -*-
"""Classes to manipulate dated monetary values.
"""

import os
import json
import time
from typing import Tuple, Union, Optional, ClassVar, Dict, Any, Type

from datetime import datetime
from decimal import Decimal
from enum import Enum
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import requests

from dmon.currency import Currency, CurrencySymbols, to_currency_enum


Numeric = Union[int, float, Decimal]


def resdir() -> str:
    return os.environ.get('MONEY_RES', '.')


def _rounded(v: Numeric) -> Decimal:
    return Decimal(int(round(v)))


def _today() -> str:
    return datetime.today().strftime('%Y-%m-%d')


def get_rates(on_date: str) -> Dict[Currency, float]:
    fname = os.path.join(resdir(), on_date + '-rates.json')
    if os.path.exists(fname):
        with open(fname, encoding='utf-8') as fin:
            data = json.load(fin)
    else:
        api_environment = 'MONEY_RATES_API_KEY'
        api_key = os.environ.get(api_environment, '')
        if not api_key:
            raise RuntimeError(
                'Need an api key for https://www.exchangerate-api.com '
                f'in the environment variable {api_environment}'
            )

        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
        if on_date != _today():
            # Requires a paid plan
            # https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY
            url = f'https://v6.exchangerate-api.com/v6/{api_key}/history/USD/' + on_date.replace(
                '-', '/'
            )

        response = requests.get(url)
        data = response.json()
        with open(fname, 'w', encoding='utf-8') as fout:
            fout.write(json.dumps(data))

    currencies = set(item.value.upper() for item in Currency)
    return {Currency(c.lower()): r for c, r in data['conversion_rates'].items() if c in currencies}


def build_rates_cache(from_date: str, to_date: str) -> None:
    print(f'Downloading rates from {from_date} to {to_date}')
    dt = date_parser.parse(from_date).date()
    to_dt = date_parser.parse(to_date).date()
    while dt <= to_dt:
        get_rates(str(dt))
        time.sleep(0.5)
        dt = dt + relativedelta(days=1)


class BaseMoney:
    on_date: ClassVar[str] = _today()
    default_currency: ClassVar[Currency] = Currency.EUR
    output_currency: Optional[Currency] = None
    rates: Optional[Dict[Currency, float]] = None

    def __init__(
        self,
        amount: Union[Numeric, Tuple[Numeric, Currency]],
        currency: Optional[Union[str, Currency]] = None,
        amount_is_cents: bool = False,
    ) -> None:
        if isinstance(amount, tuple):
            amount, currency = amount
            amount_is_cents = True

        if currency is None:
            currency = self.default_currency

        self._amount: Decimal = (
            Decimal(amount) if amount_is_cents else Decimal('100') * Decimal(amount)
        )
        self.currency: Currency = to_currency_enum(currency)

    @classmethod
    def to_date(cls, dt: str) -> None:
        cls.on_date = dt

    @classmethod
    def to_today(cls) -> None:
        cls.on_date = _today()

    def as_tuple(self) -> Tuple[Decimal, str]:
        return self._amount, self.currency.value

    def cents(self, currency: Optional[Union[str, Currency]] = None) -> Decimal:
        currency = to_currency_enum(currency or self.currency)
        if currency == self.currency:
            return self._amount

        if self.rates is None:
            self.rates = get_rates(self.on_date)

        return self._amount * Decimal(self.rates[currency]) / Decimal(self.rates[self.currency])

    def amount(
        self, currency: Optional[Union[str, Currency]] = None, rounding: bool = False
    ) -> Decimal:
        val = self.cents(currency)
        return (Decimal(round(val)) if rounding else val) / Decimal('100')

    def to(self, currency: Union[str, Currency], rounding: bool = False) -> 'BaseMoney':
        currency = to_currency_enum(currency)
        _amount = self.cents(currency)
        return self.__class__(
            Decimal(round(_amount)) if rounding else _amount, currency, amount_is_cents=True
        )

    def normalized_amounts(self, o: 'BaseMoney') -> Tuple[Decimal, Decimal, Currency]:
        """Returns the two values with which to operate, and their
        common currency. If the two currencies are the same we do not
        need to do any conversions; if they are not, they will both be
        converted to the default currency.
        """
        if self.currency == o.currency:
            return self.cents(), o.cents(), self.currency
        return (
            self.cents(self.default_currency),
            o.cents(self.default_currency),
            self.default_currency,
        )

    def __str__(self) -> str:
        # output_currency may still be None
        currency = self.output_currency or self.currency
        return '%s%.2f' % (CurrencySymbols[currency], self.amount(currency, rounding=True))

    def __repr__(self) -> str:
        return str(self)

    def __neg__(self) -> 'BaseMoney':
        return self.__class__(-self._amount / Decimal('100'), self.currency)

    def __add__(self, o: Union['BaseMoney', Numeric]) -> 'BaseMoney':
        if not isinstance(o, BaseMoney):
            o = self.__class__(Decimal(o), self.currency)

        v1, v2, out_currency = self.normalized_amounts(o)
        return self.__class__(v1 + v2, out_currency, amount_is_cents=True)

    def __radd__(self, o: Union['BaseMoney', Numeric]) -> 'BaseMoney':
        return self + o

    def __sub__(self, o: 'BaseMoney') -> 'BaseMoney':
        v1, v2, out_currency = self.normalized_amounts(o)
        return self.__class__(v1 - v2, out_currency, amount_is_cents=True)

    def __rsub__(self, o: 'BaseMoney') -> 'BaseMoney':
        return -self + o

    def __mul__(self, n: Numeric) -> 'BaseMoney':
        return self.__class__(self._amount * Decimal(n), self.currency, amount_is_cents=True)

    __rmul__ = __mul__

    def __truediv__(self, n: Union['BaseMoney', Numeric]) -> Union['BaseMoney', Decimal]:
        if isinstance(n, BaseMoney):
            return self._amount / n.to(self.currency).cents()
        return self.__class__(self._amount / Decimal(n), self.currency, amount_is_cents=True)

    def __ne__(self, o: object) -> bool:
        if not isinstance(o, BaseMoney):
            return NotImplemented
        return _rounded(self._amount) != _rounded(o.cents(self.currency))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BaseMoney):
            return NotImplemented
        return _rounded(self._amount) == _rounded(o.cents(self.currency))

    def __gt__(self, o: 'BaseMoney') -> bool:
        return _rounded(self._amount) > _rounded(o.cents(self.currency))

    def __ge__(self, o: 'BaseMoney') -> bool:
        return _rounded(self._amount) >= _rounded(o.cents(self.currency))

    def __lt__(self, o: 'BaseMoney') -> bool:
        return _rounded(self._amount) < _rounded(o.cents(self.currency))

    def __le__(self, o: 'BaseMoney') -> bool:
        return self._amount <= o.cents(self.currency)

    def __conform__(self, protocol: Any) -> Optional[str]:
        import sqlite3

        """Enables writing to an sqlite database

        https://docs.python.org/3/library/sqlite3.html#how-to-write-adaptable-objects

        Will also need the inverse (string to Money_*) to be registered with
        register_converter.
        """
        if protocol is sqlite3.PrepareProtocol:
            amount, currency = self.as_tuple()
            return f"{str(amount)};{currency}"
        return None


def Money(
    currency: Union[str, Currency] = Currency.EUR,
    output_currency: Optional[Union[str, Currency]] = None,
    on: Optional[str] = None,
    name: Optional[str] = '',
) -> Type[BaseMoney]:
    """Factory that creates a class for computing with a currency on a date."""
    class_name = name or 'Money_' + (on if on else 'latest')
    class_attrs = {
        'on_date': on or _today(),
        'default_currency': currency,
        'output_currency': to_currency_enum(output_currency) if output_currency else None,
    }
    return type(class_name, (BaseMoney,), class_attrs)


def add_args(parser):
    parser.add_argument(
        '--rates-cache',
        help=(
            'Download the conversion rates.  It has the form of a date, '
            'like 2022-04-34, or two.  If only one download until today, '
            'otherwise from the first until the second, included.'
        ),
        type=str,
        nargs='+',
        required=False,
    )


def main(args):
    if args.rates_cache:
        from_dt = args.rates_cache[0]
        to_dt = _today() if len(args.rates_cache) == 1 else args.rates_cache[1]
        build_rates_cache(from_dt, to_dt)
