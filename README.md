# dated-money — dmon.money.Money

Manipulate monetary values, each consisting in an amount (stored as a Decimal in cents) and a currency, with control on the date on which currency conversions take place.

It differs from the [money](https://pypi.org/project/money/) package in that it treats the date as a first class element.

It downloads and saves today's conversion rates from https://www.exchangerate-api.com/ using your API key (see below).  If your account is free currency exchanges will only work for today, or for dates for which a conversion rate json file is found.  If your account is paid all dates will work.

## Examples

```python
from decimal import Decimal as Dec
from dmon.money import Money, Currency

# Compute in eur with today's conversion rates (default)
Eur = Money(Currency.EUR)

# Compute in gbp with today's conversion rates
Gbp = Money('£')

assert Eur(40).cents() == Dec('4000')
assert Eur(40).to('$').cents() == Dec('4020.100502512562832012897042')
assert Eur(20) < Gbp(20)
assert Eur(20, '£') == Eur(20, 'gbp') == Eur(20, Currency.GBP) == Gbp(20)

# We can define the default date for conversions when creating the class
OldUsd = Money('$', on='2022-01-07')
assert str(OldUsd(20, 'eur').to('$')) == '$22.61'
assert str(Eur(20, 'eur').to('$')) == '$20.13'  # With today's rates

# Computations are done in the default currency of the class Eur
assert str(Eur(20, 'aud') + Eur(20, 'gbp')) == '€37.00'

# If we move to another date the values differ
Eur.to_date('2022-01-07')
assert str(Eur(20, 'aud') + Eur(20, 'gbp')) == '€36.65'

# If we use two classes with different dates the first one wins
assert str(Eur(20, 'aud') + Gbp(20, 'gbp')) == '€36.23'
assert str(Gbp(20) + Eur(20, 'aud')) == '£30.61'

assert Eur(20) / Gbp(20) == Dec('0.8500402576489532855181620688')
assert Eur(20) / 2 == Eur(10)
assert str(1.2 * Eur(20)) == '€24.00'
assert str(1.2 * Eur(20).to(Currency.CAD)) == 'C$31.53'

paid = Gbp(10)
amount, currency = paid.as_tuple()
assert (amount, currency) == (Dec('1000'), 'gbp')
assert Gbp((amount, currency)) == paid
```

## Installation

`pip install dated-money`

## Usage

The metaclass `Money` returns a class that knows its currency and the date for which currency transformations should be done.  When the `on` argument is `None` (default) the date is set to today's.  If it is a date string, like `'2021-10-29'`, it will do the conversions with the date's exchange rate (assuming that it can find the json file with the rates, otherwise it will fail).

**Important** All computations are done with cents stored as Decimal, but comparisons are are rounded to the second decimal.  So, for example,

```python
paid = Gbp(10)
paid_usd = paid.to('$')
paid_usd.cents()  # Decimal('1183.992422448496305219877141')
str(paid_usd)     # '$11.84'

# If we initialize with a string instead of a float it will be an exact Decimal.
native_usd = Gbp('11.84', 'usd')
native_usd.cents()  # Decimal('1184.00')
assert native_usd == paid_usd
assert native_usd.cents() != paid_usd.cents()
native_usd.cents() - paid_usd.cents()  # Decimal('0.007577551503694780122859')
```

## Environment variables

The `MONEY_RATES_API_KEY` environment variable contains your API key for [https://your_exchangerate-api.com](the exchange rates provider).

`export MONEY_RATES_API_KEY=your_exchangerate-api.com_key`

The exchange rates will only be downloaded once a day, and cached in the directory pointed at by `MONEY_RES`, if defined, or the current directory otherwise.

`export MONEY_RES=a/resources/directory`
