# money

```python
from decimal import Decimal as Dec
from money.money import Money, Currency

Eur = Money(Currency.EUR)
Gbp = Money('£')
OldUsd = Money('$', on='2022-01-07')

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
