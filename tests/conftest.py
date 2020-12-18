"""Pytest configuration"""
import sys
from pathlib import Path

import pytest  # type: ignore

sys.path.insert(0, str(Path.cwd().parent))

from src.reports import Reports  # pylint:disable=wrong-import-position,wrong-import-order  # noqa: E402


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
    return Reports(username, password)
