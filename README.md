# dmon.Money

Manipulate monetary values, each consisting in an amount (stored as a Decimal in cents), a currency, and a date.

It differs from the [money](https://pypi.org/project/money/) package in that it treats the date as a first class element: the value of a dollar changes with time.

It downloads and saves today's conversion rates from https://www.exchangerate-api.com/ using your API key (see below).  Currency exchanges will only work for today, or for dates in which a conversion rate json file is found.

```python
from decimal import Decimal as Dec
from dmon.money import Money, Currency

Eur = Money(Currency.EUR)
Gbp = Money('£')
OldUsd = Money('$', today='2022-01-07')

assert Eur(40).cents() == Dec('4000')
assert Eur(40).to('$').cents() == Dec('4020.100502512562832012897042')
assert Eur(20) < Gbp(20)
assert Eur(20) / Gbp(20) == Dec('0.8468856398958541665600293862')
assert Eur(20) / 2 == Eur(10)
assert str(1.2 * Eur(20)) == '€24.00'
assert str(1.2 * Eur(20).to('C$')) == 'C$31.53'

paid = Gbp(10)
amount, currency, on_date = paid.as_tuple()
assert (amount, currency, on_date) == (Dec('1000'), 'gbp', '2022-07-15')
assert Gbp((amount, currency, on_date)) == paid
```

The metaclass `Money` returns a class that knows its currency and the date for which currency transformations should be done.  When the `today` argument is `None` (default) the date of each instance is respected.  If it is `True` the conversions are done using today's exchange rate; if it is a date string, like `'2021-10-29'`, it will do the conversions with the date's exchange rate (assuing that it can find the json file with the rates).

So if you want to know the impact of changes in exchange rates you can do your computations with two money classes, one with `today=None` and one with `today=True`, and compare the resulta.

**Important** All computations are done with cents stored as Decimal, but comparisons are are rounded to the second decimal.  So, for example,

```
paid = Gbp(10)
paid_usd = paid.to('$')
paid_usd.cents()  # Decimal('1182.452406290646791283108172')
str(paid_usd)     # '$11.82'

Usd = Money('$')

# If you initialize with a string instead of a float it will be an exact Decimal.
native_usd = Usd('11.82')
native_usd.cents()  # Decimal('1182.00')
assert native_usd == paid_usd
```

## Installation

## Virtual environment

Create the virtual environment:

`mkdir -p ~/venv/money && python -m venv ~/venv/money`

or maybe

`mkdir -p ~/venv/money && /usr/local/bin/python3.9 -m venv ~/venv/money`

and activate it:

`source ~/venv/money/bin/activate`

## Install

To install the dependencies in editable mode:

`pip install -e .`

To install the development dependencies (including testing):

`pip install ".[dev]"`

## Running

First set up the environment values:

`export MONEY_RATES_API_KEY=your_exchangerate-api.com_key`
`export MONEY_RES=a/resources/directory`
