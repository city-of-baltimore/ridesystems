"""
Tests ridesystems.py

Should be called as test_ridesystems.py --username <username> --password <password>
"""

from datetime import datetime, timedelta

import logging
import pytest

from .. import ridesystems  # pylint:disable=relative-beyond-top-level


logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')


def test_login_failure():
    """Tests for login with bad username/password, which throws an exception"""
    with pytest.raises(AssertionError):
        ridesystems.Scraper('invalidusername', 'invalidpassword')


def test_get_otp(username, password):
    """
    Validate that we get valid data when we pull the on time performance data

    Expected format
    [[date, route, block_id, vehicle, stop, scheduled_dept_time, actual_dept_time],
    ...]
    """
    start_date = datetime.today() - timedelta(days=1)
    end_date = datetime.today() - timedelta(days=1)

    rs_cls = ridesystems.Scraper(username, password)
    otp_data = rs_cls.get_otp(start_date, end_date)

    iters = 0
    for row in otp_data:
        assert isinstance(datetime.strptime(row['date'], '%m/%d/%Y'), datetime)
        assert row['route'] is not None
        assert row['stop'] is not None
        assert row['blockid'] is not None
        assert row['scheduledarrivaltime'] is not None
        assert row['actualarrivaltime'] is not None
        assert row['scheduleddeparturetime'] is not None
        assert row['actualdeparturetime'] is not None
        assert row['ontimestatus'] is not None
        assert row['vehicle'] is not None
        iters += 1

    assert iters > 50


def test_get_otp_apr_6(username, password):
    """
    Validate that we get valid data when we pull the on time performance data

    Expected format
    [[date, route, block_id, vehicle, stop, scheduled_dept_time, actual_dept_time],
    ...]
    """
    start_date = datetime(2020, 4, 6)
    end_date = datetime(2020, 4, 6)

    rs_cls = ridesystems.Scraper(username, password)
    otp_data = rs_cls.get_otp(start_date, end_date)

    iters = 0
    for row in otp_data:
        assert isinstance(datetime.strptime(row['date'], '%m/%d/%Y'), datetime)
        assert row['route'] is not None
        assert row['stop'] is not None
        assert row['blockid'] is not None
        assert row['scheduledarrivaltime'] is not None
        assert row['actualarrivaltime'] is not None
        assert row['scheduleddeparturetime'] is not None
        assert row['actualdeparturetime'] is not None
        assert row['ontimestatus'] is not None
        assert row['vehicle'] is not None
        iters += 1

    assert iters > 50


def test_parse_ltiv_data(username, password):
    """Tests the parse_ltiv_data method"""
    rs_cls = ridesystems.Scraper(username, password)

    expect = {'Return': ('this', 'NONE')}
    actual = rs_cls.parse_ltiv_data('4|NONE|Return|this|')
    assert compare_ltiv_data(expect, actual), \
        'Did not pass basic assertion. Expected {}. Got {}'.format(expect, actual)

    with pytest.raises(AssertionError):
        rs_cls.parse_ltiv_data('4|NONE|Return|this')

    expect = {'Return': ('this', 'NONE'), 'Something': ('abcdefghijklmnop', 'NONE')}
    actual = rs_cls.parse_ltiv_data('4|NONE|Return|this|16|NONE|Something|abcdefghijklmnop|')
    assert compare_ltiv_data(expect, actual), \
        'Did not pass second assertion. Expected {}. Got {}'.format(expect, actual)

    with pytest.raises(AssertionError):
        rs_cls.parse_ltiv_data('3|NONE|Return|this|7|NONE|x|xxxxxxx|')

    expect = {'Return': ('this', 'NONE'), 'x': ('xxx|xxx', 'NONE')}
    actual = rs_cls.parse_ltiv_data('4|NONE|Return|this|7|NONE|x|xxx|xxx|')
    assert compare_ltiv_data(expect, actual), \
        'Did not pass extra delimiter test. Expected {}. Got {}'.format(expect, actual)

    expect = {}
    actual = rs_cls.parse_ltiv_data('')
    assert compare_ltiv_data(expect, actual), 'Empty case failed. Expected {}. Got {}'.format(expect, actual)

    expect = {'': ('', '')}
    actual = rs_cls.parse_ltiv_data('0||||')
    assert compare_ltiv_data(expect, actual), 'Did not pass basic assertion. Expected {}. Got {}'.format(expect, actual)


def compare_ltiv_data(expected, actual):
    """
    Helper to test the LENGTH|TYPE|ID|VALUE data. It is packed in a dictionary like
    {ID: (VALUE, TYPE)
    """
    for k, val in expected.items():
        actual_v = actual.pop(k)
        if not (actual_v[0] == val[0] and actual_v[1] == val[1]):
            return False
    return actual == {}
