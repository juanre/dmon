# -*- coding: utf-8 -*-

import os
import json
import threading
import time
import subprocess
import sqlite3
from contextlib import contextmanager
from typing import Optional, Union, Dict, List, Set, ClassVar

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import requests

from dmon.currency import Currency


import threading
import sqlite3


class ConnectionPool:
    _instance = None
    _lock = threading.Lock()
    _db_file: ClassVar[str] = ''
    _ref_count: ClassVar[int] = 0
    _connection = None

    def __new__(cls, db_file: str):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._db_file = db_file
        return cls._instance

    @classmethod
    def get_connection(cls):
        with cls._lock:
            if cls._connection is None:
                cls._connection = sqlite3.connect(cls._db_file)
                cls._connection.row_factory = sqlite3.Row
            cls._ref_count += 1
            return cls._connection

    @classmethod
    def release_connection(cls):
        with cls._lock:
            cls._ref_count -= 1
            if cls._ref_count == 0 and cls._connection is not None:
                cls._connection.close()
                cls._connection = None


CONNECTION_POOL = None


@contextmanager
def get_db_connection(database_dir: Optional[str] = None):
    global CONNECTION_POOL
    if CONNECTION_POOL is None:
        ddir = database_dir or os.environ.get('DMON_RATES_CACHE', '.')
        os.makedirs(ddir, exist_ok=True)
        CONNECTION_POOL = ConnectionPool(os.path.join(ddir, 'exchange-rates.db'))

    connection = CONNECTION_POOL.get_connection()
    try:
        yield connection
    finally:
        CONNECTION_POOL.release_connection()


def create_cache_table(currency_names: Union[List[str], Set[str]]):
    columns = ', '.join(f'"{currency.lower()}" REAL' for currency in currency_names)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'''
            CREATE TABLE IF NOT EXISTS rates (
                date TEXT PRIMARY KEY,
                {columns}
            )
        '''
        )
        conn.commit()


def maybe_create_cache_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        columns = ', '.join(f'"{currency.value}" REAL' for currency in Currency)
        cursor.execute(
            f'''CREATE TABLE IF NOT EXISTS rates (
                       date TEXT PRIMARY KEY, {columns}
                )
            '''
        )
        conn.commit()


def cache_day_rates(date: str, rates: Dict[str, float]):
    maybe_create_cache_table()
    with get_db_connection() as conn:
        valid_currencies = {currency.value for currency in Currency}
        filtered_rates = {
            currency: rate
            for currency, rate in rates.items()
            if currency.lower() in valid_currencies
        }

        columns = ', '.join(f'"{currency.lower()}"' for currency in filtered_rates.keys())
        placeholders = ', '.join('?' * len(filtered_rates))
        values = tuple(filtered_rates.values())

        cursor = conn.cursor()
        cursor.execute(
            f"INSERT OR REPLACE INTO rates (date, {columns}) VALUES (?, {placeholders})",
            (date, *values),
        )
        conn.commit()


def fill_cache_db():
    maybe_create_cache_table()
    repo_dir = os.environ.get('DMON_RATES_REPO')
    if repo_dir is None:
        raise ValueError("DMON_RATES_REPO environment variable is not set")

    for filename in os.listdir(os.path.join(repo_dir, 'money')):
        if filename.endswith('-rates.json'):
            file_path = os.path.join(repo_dir, 'money', filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                rates = data['conversion_rates']
                date = filename.split('-rates.json')[0]
                cache_day_rates(date, rates)


def get_day_rates_from_repo(on_date: str) -> Optional[Dict[str, float]]:
    """Fetches exchange rates from a local git repository for a given
    date. It looks for the repository in the environment variable
    DMON_RATES_REPO, and the rates file in
    money/yyyy-mm-dd-rates.json.

    The rates file is a json that contains a dictionary like:

    {
     "conversion_rates":{
      "USD":1,
      "AED":3.6725,
      "AFN":71.3141,
    ...}
    }

    Args:

        on_date: The date for which to fetch the exchange rates, in
        'YYYY-MM-DD' format.

    Returns:

        The exchange rates as a dictionary, or None if the rates
        cannot be found for the specified date.

    Environment variables:

        DMON_RATES_REPO: directory containing a git repository with
            the rates files in the money subdirectory.

    """
    print('Attempting to get rates from repo')
    repo_dir = os.environ.get('DMON_RATES_REPO', None)
    if repo_dir is None or not os.path.exists(repo_dir):
        return None

    rates_file_path = os.path.join(repo_dir, 'money', on_date + '-rates.json')
    if not os.path.exists(rates_file_path):
        # Attempt to update the local repository
        try:
            print('Pulling exchange rates repo')
            subprocess.run(
                ['git', '-C', repo_dir, 'pull'],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            return None

    if os.path.exists(rates_file_path):
        with open(rates_file_path, 'r', encoding='utf-8') as file:
            rates = json.load(file)
            return rates['conversion_rates']

    return None


def today() -> str:
    return datetime.today().strftime('%Y-%m-%d')


def fetch_rates_from_exchangerate_api(on_date: str) -> Optional[Dict[str, float]]:
    """Fetches currency exchange rates from exchangerate_api.com.

    Args:

        on_date: The date for which to fetch the exchange rates,
        in 'YYYY-MM-DD' format.

    Returns:

        A dictionary mapping `Currency` enum members to their exchange
        rate against a base currency (usually USD) for the specified
        date. Returns None if the rates cannot be fetched.

    Raises:

        RuntimeError: If the API key is not found in the environment
        variable `MONEY_RATES_API_KEY` when attempting to download
        rates from the external API.

    Environment variables:

        DMON_EXCHANGERATE_API_KEY: API key for https://exchangerate-api.com.

    The external API used for downloading rates
    (https://exchangerate-api.com) may require a paid plan for
    accessing historical data.

    """

    api_environment = 'DMON_EXCHANGERATE_API_KEY'
    api_key = os.environ.get(api_environment, '')
    if not api_key:
        raise RuntimeError(
            'Need an api key for https://www.exchangerate-api.com '
            f'in the environment variable {api_environment}'
        )

    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
    if on_date != today():
        # Requires a paid plan
        # https://v6.exchangerate-api.com/v6/YOUR-API-KEY/history/USD/YEAR/MONTH/DAY
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/history/USD/' + on_date.replace(
            '-', '/'
        )

    response = requests.get(url)

    if response.status_code == 200:  # Checks if the request was successful
        rates = response.json()
        # Checks if 'conversion_rates' is in the response and returns it, otherwise returns None
        return rates.get('conversion_rates')
    else:
        # Log or handle unsuccessful request appropriately
        print(f"Failed to fetch rates for {on_date}: HTTP {response.status_code}")
        return None


def get_rates(on_date: str, *currencies: Currency) -> Optional[Dict[Currency, Optional[float]]]:
    """Retrieves the exchange rates for the specified currencies on a
    given date.

    This function first attempts to fetch the rates from the local
    database.  If the rates for the given date are not found in the
    database, it then tries to retrieve them from a repository. If the
    rates are still not found, it makes a call to the exchangerate_api
    to fetch the rates. Once fetched from the repository or the API,
    the rates are cached in the local database for future use.

    Args:

        on_date: The date for which to fetch the exchange rates, in
                 'YYYY-MM-DD' format.

        *currencies: Variable length argument list of Currency enum
                     members for which to fetch the exchange rates.

    Returns:

        A dictionary mapping each requested currency to its exchange
        rate against the base currency for the specified date. The
        rate is `None` if it could not be fetched.

    Raises:

        RuntimeError: If the required API key for exchangerate_api.com
                      is not found in the environment variable
                      `MONEY_RATES_API_KEY` when attempting to
                      download rates from the external API.

    Environment variables:

        DMON_RATES_CACHE: directory where the cache file (sqlite
            database) is stored.

        DMON_EXCHANGERATE_API_KEY: API key for
            https://exchangerate-api.com

        DMON_RATES_REPO: directory containing a git repository with
            the rates files in a money subdirectory.

    The external API used for downloading rates
    (https://exchangerate-api.com) may require a paid plan for
    accessing historical data. The function makes use of environment
    variables for configuration and may need internet access to
    retrieve rates from the external API.

    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        placeholders = ', '.join(f'"{currency.value}"' for currency in currencies)
        if not placeholders:
            placeholders = '*'
        cursor.execute(f'SELECT {placeholders} FROM rates WHERE date = ?', (on_date,))
        row = cursor.fetchone()

        if row:
            return {currency: row[i] for i, currency in enumerate(currencies)}
        else:
            # If the day doesn't have a row in the database, try to get it from the repo
            rates = get_day_rates_from_repo(on_date)
            if not rates:
                # If not there try to get it from exchangerate_api
                rates = fetch_rates_from_exchangerate_api(on_date)

            if rates:
                cache_day_rates(on_date, rates)
                return {currency: rates.get(currency.value.upper()) for currency in currencies}

            return None


def get_rate(on_date: str, currency: Currency) -> Optional[float]:
    rate = get_rates(on_date, currency)
    if rate is not None:
        return rate[currency]

    return None


def fetch_period_rates(from_date: str, to_date: str) -> None:
    """Builds a rates cache by querying the rates for each day in a
    period. If you don't have a repository with the conversion rates
    json files, it will attempt to download them from
    exchangerate_api.com.

    You will need a paid API key for this.

    Args:

        from_date: First date to add to the cache, in yyyy-mm-dd format.

        to_date: Last date to add to the cache, in yyyy-mm-dd format.
    """
    print(f'Downloading rates from {from_date} to {to_date}')
    dt = date_parser.parse(from_date).date()
    to_dt = date_parser.parse(to_date).date()
    while dt <= to_dt:
        get_rates(str(dt))
        time.sleep(0.5)
        dt = dt + relativedelta(days=1)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Currency Conversion Cache Management')
    parser.add_argument(
        '-C',
        '--update-cache',
        action='store_true',
        help='Update the currency rates cache database',
    )
    parser.add_argument(
        '--create-table',
        action='store_true',
        help='Create the currency rates cache table',
    )
    parser.add_argument(
        '-r',
        '--rate-on',
        help='Retrieve the exchange rate[s] on date (YYYY-MM-DD)',
    )
    parser.add_argument(
        '-c', '--currency', help='Optional: Currency for which to retrieve the exchange rate'
    )
    parser.add_argument(
        '--fetch-rates',
        help='Retrieve the exchange rates of all the days in a period. Format YYYY-MM-DD:YYYY-MM-DD',
    )

    args = parser.parse_args()

    if args.create_table:
        print("Updating currency conversion cache database...")
        maybe_create_cache_table()
        print("Cache database updated successfully.")

    if args.update_cache:
        print("Updating currency conversion cache database...")
        fill_cache_db()
        print("Cache database updated successfully.")

    if args.fetch_rates:
        from_dt, to_dt = args.fetch_rates.split(':')
        fetch_period_rates(from_dt, to_dt)

    rate_on_date = args.rate_on
    currency = args.currency

    if rate_on_date:
        if currency:
            currency = Currency(currency.lower())
            rate = get_rate(rate_on_date, currency)
            if rate is not None:
                print(f'Exchange rate for {currency} on {rate_on_date}: {rate}')
            else:
                print(f'Exchange rate not found for {currency} on {rate_on_date}')
        else:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM rates WHERE date = ?', (rate_on_date,))
                row = cursor.fetchone()
                if row:
                    rates = {Currency(k.lower()): v for k, v in zip(row.keys()[1:], row[1:])}
                    print(f'Exchange rates on {rate_on_date}:')
                    for currency, rate in rates.items():
                        print(f'{currency}: {rate}')
                else:
                    print(f'Exchange rates not found for {rate_on_date}')


if __name__ == '__main__':
    main()
