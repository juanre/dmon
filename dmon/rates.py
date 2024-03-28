# -*- coding: utf-8 -*-

import os
import json
import time
import subprocess

from typing import Optional, Dict

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import requests

from dmon.currency import Currency


def today() -> str:
    return datetime.today().strftime('%Y-%m-%d')


def rates_file_name(on_date: str) -> str:
    """The rates file is a json that contains a dictionary like:

    {
     "conversion_rates":{
      "USD":1,
      "AED":3.6725,
      "AFN":71.3141,
    ...}
    }

    """
    return on_date + '-rates.json'


def rates_download_file(on_date: str) -> str:
    """The file name where rates for a given date are stored.

    Args:
        on_date (str): The date for which to fetch the exchange rates, in 'YYYY-MM-DD' format.

    Returns:
        The full file name of the rates file.

    """
    return os.path.join(os.environ.get('DMON_RATES_CACHE', '.'), rates_file_name(on_date))


def get_downloaded_rates(on_date: str) -> Optional[Dict[str, Dict]]:
    """Returns the downloaded rates for a day, if existing. It looks
    for the rates file in the directory pointed to by the
    DMON_RATES_CACHE environment variable, or the current directory
    if the environment variable is not set.

    Args:
        on_date (str): The date for which to fetch the exchange rates, in 'YYYY-MM-DD' format.

    Returns:
        Optional[Dict[str, Dict]]: The exchange rates as a dictionary, or None if the rates
        cannot be found for the specified date.

    """
    fname = rates_download_file(on_date)
    if os.path.exists(fname):
        with open(fname, encoding='utf-8') as fin:
            return json.load(fin)

    return None


def get_repo_rates(on_date: str) -> Optional[Dict[str, Dict]]:
    """Fetches exchange rates from a local git repository for a given
    date. It looks for the repository in the environment variable
    DMON_RATES_REPO, and the rates file in
    money/yyyy-mm-dd-rates.json.

    Args:
        on_date (str): The date for which to fetch the exchange rates, in 'YYYY-MM-DD' format.

    Returns:
        Optional[Dict[str, Dict]]: The exchange rates as a dictionary, or None if the rates
        cannot be found for the specified date.
    """
    repo_dir = os.environ.get('DMON_RATES_REPO', None)
    if repo_dir is None or not os.path.exists(repo_dir):
        return None

    # Attempt to update the local repository
    try:
        subprocess.run(
            ['git', '-C', repo_dir, 'pull'],
            check=True,
            stdout=subprocess.DEVNULL,  # Silence standard output
            stderr=subprocess.DEVNULL,  # Silence standard error
        )
    except subprocess.CalledProcessError:
        # Handle errors in updating the repo, e.g., network issues, permissions, etc.
        return None

    # Construct the file path for the rates file
    rates_file_path = os.path.join(repo_dir, 'money', rates_file_name(on_date))
    if not os.path.exists(rates_file_path):
        return None

    # Load and return the rates file
    with open(rates_file_path, 'r', encoding='utf-8') as file:
        rates = json.load(file)
        return rates


def get_rates(on_date: str) -> Optional[Dict[Currency, float]]:
    """Fetches currency exchange rates for a given date, attempting
    to retrieve them from locally downloaded data, a git repository,
    or an external API as a fallback.

    This function first tries to find the exchange rates for the
    specified date in locally downloaded files. If not found, it
    checks a configured git repository. As a last resort, it attempts
    to download the day's exchange rates from an external API, which
    requires an API key set in an environment variable.

    The rates files are expected to be called yyyy-mm-dd-rates.json,
    and contain a dictionary like:

    {
     "conversion_rates":{
      "USD":1,
      "AED":3.6725,
      "AFN":71.3141,
    ...}
    }

    Args:
        on_date (str): The date for which to fetch the exchange rates,
        in 'YYYY-MM-DD' format.

    Returns:
        Optional[Dict[Currency, float]]: A dictionary mapping
        `Currency` enum members to their exchange rate against a base
        currency (usually USD) for the specified date. Returns None if
        the rates cannot be found or downloaded.

    Raises:
        RuntimeError: If the API key is not found in the environment
        variable `MONEY_RATES_API_KEY` when attempting to download
        rates from the external API.

    Environment variables:

        DMON_RATES_CACHE: directory where rates are
            downloaded. Defaults to '.'

        DMON_RATES_REPO: directory containing a git repository with
            the rates files in the money subdirectory.

        DMON_EXCHANGERATE_API_KEY: API key for https://exchangerate-api.com.

    Note:
        The external API used for downloading rates
        (https://exchangerate-api.com) may require a paid plan for
        accessing historical data.

    """

    rates = get_downloaded_rates(on_date) or get_repo_rates(on_date)

    if not rates:
        # Attempt to download the day's rates.
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
        rates = response.json()
        with open(rates_download_file(on_date), 'w', encoding='utf-8') as fout:
            fout.write(json.dumps(rates))

    if rates:
        currencies = set(item.value.upper() for item in Currency)
        return {
            Currency(c.lower()): r for c, r in rates['conversion_rates'].items() if c in currencies
        }

    return None


def build_rates_cache(from_date: str, to_date: str) -> None:
    print(f'Downloading rates from {from_date} to {to_date}')
    dt = date_parser.parse(from_date).date()
    to_dt = date_parser.parse(to_date).date()
    while dt <= to_dt:
        get_rates(str(dt))
        time.sleep(0.5)
        dt = dt + relativedelta(days=1)
