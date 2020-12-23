"""Pytest configuration"""
import pytest  # type: ignore

from ridesystems.reports import Reports
from ridesystems.api import API


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
