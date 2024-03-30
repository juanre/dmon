import os
import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('DMON_RATES_REPO', 'test/res')
    monkeypatch.setenv('DMON_RATES_CACHE', 'test/res')
