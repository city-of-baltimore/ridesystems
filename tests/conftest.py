"""Pytest configuration"""
import pytest


def pytest_addoption(parser):
    """Adds command line options"""
    parser.addoption("--username", action="store")
    parser.addoption("--password", action="store")


@pytest.fixture
def username(request):
    """Username fixture"""
    return request.config.getoption("username")


@pytest.fixture
def password(request):
    """Password fixture"""
    return request.config.getoption("password")
