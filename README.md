# Dated Money

Dated Money is a Python library for manipulating monetary values with control over the date on which currency conversions take place. It represents each monetary value as an amount (stored as a Decimal in cents) and a currency, along with a corresponding date.

It differs from the [money](https://pypi.org/project/money/) package in that it treats the date as a
first-class element.

It downloads and saves today's conversion rates from https://www.exchangerate-api.com/ using your API key (see below).  You may need a paid account for the fetching of rates for days other than today to work.


## Features

- Perform arithmetic operations on monetary values with different currencies and dates
- Convert monetary values between currencies based on exchange rates for specific dates
- Fetch and cache exchange rates from external APIs or local repositories
- Flexible configuration through environment variables

## Installation

You can install Dated Money using pip:

```
pip install dated-money
```

## Usage

### Basic Examples

```python
from decimal import Decimal as Dec
from dmon import Money, Currency

# Create a Money class with EUR as the base currency and conversion rates from a specific date
date_a = '2022-07-14'
Eur = Money(Currency.EUR, date_a)

# Create a Money class with AUD as the base currency and conversion rates from the same date
Aud = Money(base_currency='A$', base_date=date_a)

# Create monetary values in different currencies
price_eur = Eur(100)  # €100
price_usd = Eur(120, Currency.USD)  # $120
price_gbp = Eur(80, '£')  # £80

# Values are stored in cents and can be accessed in any currency
assert Eur(23, '€').cents('eur') == 2300
assert Eur(40).cents('usd') == Dec('4020.100502512562832012897042')

# Values can be created in any currency, regardless of the base currency
assert Eur(20, '£') == Aud(20, '£')

# Perform arithmetic operations
total = price_eur + price_usd + price_gbp
assert str(total) == '€270.40'  # Total in the base currency (EUR)

# Convert to a specific currency
total_usd = total.to(Currency.USD)
assert str(total_usd) == '$303.89'

# Compare monetary values
assert price_eur < price_usd
assert price_gbp == Eur(80, Currency.GBP)
```

### Operations with Different Currencies and Dates

You can perform operations on monetary values with different currencies and conversion dates:

```python
date_a = '2022-07-14'
date_b = '2022-01-07'

Eur = Money(Currency.EUR, date_a)
OldEur = Money('€', date_b)
Aud = Money(Currency.AUD, date_a)

# Operations between instances with different dates return an instance with the base date of the first element
adds = OldEur(10) + Eur(30)
assert adds.amount() == 40
assert adds.on_date == OldEur.base_date

# Operations between instances with different currencies return a result in the base currency
result = Eur(10, '$') + Eur(20, 'CAD')
assert result.currency == Currency.EUR

# Changing the reference dates affects the operation results
assert Eur(10, '$', date_a) + Eur(20, 'CAD', date_a) != Eur(10, '$', date_b) + Eur(20, 'CAD', date_b)

# Perform various arithmetic operations
assert Aud(10) + Eur(20) == Aud(39.70) == Eur(39.7, 'aud')
assert Eur(20) + Aud(10) == Eur(26.73)
assert (Aud(10) + Eur(20)).currency == Currency.AUD
assert (Eur(20) + Aud(10)).currency == Currency.EUR
assert Eur(20, 'aud') + Eur(20, 'gbp') == Aud(20, 'aud') + Aud(20, 'gbp')
```

### Using a Single Money Class

In normal use, you will probably create a single Money class with your preferred base currency and use it to handle monetary values in various currencies:

```python
Eur = Money(Currency.EUR)

price_eur = Eur(100)  # €100
price_usd = Eur(120, Currency.USD)  # $120
price_gbp = Eur(80, '£')  # £80

total = price_eur + price_usd + price_gbp
assert str(total) == '€304.71'  # Total in the base currency (EUR)

assert price_usd.currency == Currency.USD
assert price_gbp.currency == Currency.GBP
```

### Configuring Exchange Rates

Dated Money provides flexibility in configuring exchange rates through environment variables:

- `DMON_RATES_CACHE`: Set this to a directory where the library can maintain a cache of exchange rates (stored in an SQLite database).

- `DMON_EXCHANGERATE_API_KEY`: If the rates file for a given date is not found in the repository or cache, the library will attempt to download it from https://exchangerate-api.com. Set this environment variable to your API key. Note that you may need a paid account to download historical data.

- `DMON_RATES_REPO`: Set this to a directory containing a git repository with the exchange rates in a `money` subdirectory. The rates should be stored in files named `yyyy-mm-dd-rates.json`, and contain a dictionary like:


```
    {
     "conversion_rates":{
      "USD":1,
      "AED":3.6725,
      "AFN":71.3141,
    ...}
    }
```

### Creating the Cache Database

To create the cache database, follow these steps:

1. Set the `DMON_RATES_CACHE` environment variable:
   ```
   export DMON_RATES_CACHE=~/.dmon
   ```

2. Create the database cache table:
   ```
   dmon-rates --create-table
   ```

If you have a paid API key for https://exchangerate-api.com, you can set the `DMON_EXCHANGERATE_API_KEY` environment variable and create your cache with:

```
dmon-rates --fetch-rates 2021-10-10:2021-10-20
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/juanre/dmon).

## License

Dated Money is released under the [MIT License](https://opensource.org/licenses/MIT).
