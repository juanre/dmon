# money


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
