"""Pytest configuration"""
import sys
from pathlib import Path

import pytest  # type: ignore

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reports import Reports  # pylint:disable=wrong-import-position,wrong-import-order  # noqa: E402
from src.api import API  # pylint:disable=wrong-import-position,wrong-import-order  # noqa: E402


def pytest_addoption(parser):
    """Adds command line options"""
    parser.addoption("--username", action="store")
    parser.addoption("--password", action="store")


@pytest.fixture(name='username')
def username_fixture(request):
    """Username fixture"""
    return request.config.getoption("username")


@pytest.fixture(name='password')
def password_fixture(request):
    """Password fixture"""
    return request.config.getoption("password")


@pytest.fixture(name='reports_fixture')
def fix_report(username, password):
    """Setup for the tests"""
    assert username, "Username required (use --username)"
    assert password, "Password required (use --password)"
    return Reports(username, password)


@pytest.fixture
def ridesystems_api():
    """Fixture for the Ridesystems API object"""
    return API('xx')  # Ridesystems doesn't actually check the API key
