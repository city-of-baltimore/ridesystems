"""
Tests ridesystems.py

Should be called as test_ridesystems.py --username <username> --password <password>
"""

import pytest

from .. import ridesystems


def test_login_success(username, password):
    """Tests for successful login, with no error thrown"""
    ridesystems.Ridesystems(username, password)


def test_login_failure():
    """Tests for login with bad username/password, which throws an exception"""
    with pytest.raises(AssertionError):
        ridesystems.Ridesystems("invalidusername", "invalidpassword")
