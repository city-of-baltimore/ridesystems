"""
Tests reports.py

Should be called as tox -- --username <username> --password <password>
"""

from datetime import datetime, time, timedelta

import pandas as pd
import pytest  # type: ignore

from ridesystems.reports import Reports


def test_login_failure():
    """Tests for login with bad username/password, which throws an exception"""
    with pytest.raises(AssertionError):
        Reports('invalidusername', 'invalidpassword')


def test_get_otp_all(reports_fixture):
    """
    Validate that we get valid data when we pull the on time performance data

    Expected format
    [[date, route, block_id, vehicle, stop, scheduled_dept_time, actual_dept_time],
    ...]
    """
    start_date = datetime.today() - timedelta(days=1)
    end_date = datetime.today() - timedelta(days=1)

    otp_data = reports_fixture.get_otp(start_date, end_date, '11, 12')

    iters = 0
    routes = set()
    stops = set()
    blockid = set()
    ontimestatuses = set()
    vehicles = set()

    for _, row in otp_data.iterrows():
        assert isinstance(row['date'], datetime)
        assert isinstance(row['route'], str)
        assert row['route'] in ['Green', 'Banner', 'Purple', 'Orange']
        assert isinstance(row['stop'], str)
        assert isinstance(row['blockid'], str)
        assert isinstance(row['scheduledarrivaltime'], time) or row['scheduledarrivaltime'] is pd.NaT
        assert isinstance(row['actualarrivaltime'], time) or row['actualarrivaltime'] is pd.NaT
        assert isinstance(row['scheduleddeparturetime'], time) or row['scheduleddeparturetime'] is pd.NaT
        assert isinstance(row['actualdeparturetime'], time) or row['actualdeparturetime'] is pd.NaT
        assert isinstance(row['ontimestatus'], str)
        assert isinstance(row['vehicle'], str)

        routes.add(row['route'])
        stops.add(row['stop'])
        blockid.add(row['blockid'])
        ontimestatuses.add(row['ontimestatus'])
        vehicles.add(row['vehicle'])
        iters += 1

    assert iters > 700
    assert len(routes) >= 4
    assert len(stops) >= 50
    assert len(blockid) >= 4
    assert len(ontimestatuses) == 4
    assert len(vehicles) > 5


def test_get_otp_apr_6(reports_fixture):
    """
    Validate that we get valid data when we pull the on time performance data. April 6 was when RideSystems was doing
    some odd stuff with their data, so its a good edge-case

    Expected format
    [[date, route, block_id, vehicle, stop, scheduled_dept_time, actual_dept_time],
    ...]
    """
    start_date = datetime(2020, 4, 6)
    end_date = datetime(2020, 4, 6)

    otp_data = reports_fixture.get_otp(start_date, end_date, '11, 12')

    iters = 0
    for _, row in otp_data.iterrows():
        assert isinstance(row['date'], datetime)
        assert isinstance(row['route'], str)
        assert row['route'] in ['Green', 'Banner', 'Purple', 'Orange']
        assert isinstance(row['stop'], str)
        assert isinstance(row['blockid'], str)
        assert isinstance(row['scheduledarrivaltime'], time) or row['scheduledarrivaltime'] is pd.NaT
        assert isinstance(row['actualarrivaltime'], time) or row['actualarrivaltime'] is pd.NaT
        assert isinstance(row['scheduleddeparturetime'], time) or row['scheduleddeparturetime'] is pd.NaT
        assert isinstance(row['actualdeparturetime'], time) or row['actualdeparturetime'] is pd.NaT
        assert isinstance(row['ontimestatus'], str)
        assert isinstance(row['vehicle'], str)
        iters += 1

    assert iters > 50


def test_get_runtimes(reports_fixture):
    """Test get_runtimes"""
    start_date = datetime.today() - timedelta(days=1)
    end_date = datetime.today() - timedelta(days=1)

    runtime_data = reports_fixture.get_runtimes(start_date, end_date)

    iters = 0
    for _, row in runtime_data.iterrows():
        assert isinstance(row['start_time'], datetime)
        assert isinstance(row['end_time'], datetime)
        assert isinstance(row['route'], str)
        assert row['route'] in ['Green', 'Banner', 'Purple', 'Orange']
        assert isinstance(row['vehicle'], str)
        iters += 1

    assert iters > 50


def test_get_ridership(reports_fixture):
    """Test get_ridership"""
    start_date = datetime.today() - timedelta(days=1)
    end_date = datetime.today() - timedelta(days=1)

    ridership_data = reports_fixture.get_ridership(start_date, end_date)

    iters = 0
    for _, row in ridership_data.iterrows():
        assert isinstance(row['vehicle'], str)
        assert isinstance(row['route'], str)
        assert row['route'] in ['Green', 'Banner', 'Purple', 'Orange']
        assert isinstance(row['stop'], str)
        assert isinstance(row['latitude'], float)
        assert isinstance(row['longitude'], float)
        assert isinstance(row['datetime'], datetime)
        assert isinstance(row['entries'], int)
        assert isinstance(row['exits'], int)
        iters += 1

    assert iters > 3000


def test_parse_ltiv_data(reports_fixture):
    """Tests the parse_ltiv_data method"""
    expect = {'Return': ('this', 'NONE')}
    actual = reports_fixture.parse_ltiv_data('4|NONE|Return|this|')
    assert compare_ltiv_data(expect, actual), \
        'Did not pass basic assertion. Expected {}. Got {}'.format(expect, actual)

    with pytest.raises(AssertionError):
        reports_fixture.parse_ltiv_data('4|NONE|Return|this')

    expect = {'Return': ('this', 'NONE'), 'Something': ('abcdefghijklmnop', 'NONE')}
    actual = reports_fixture.parse_ltiv_data('4|NONE|Return|this|16|NONE|Something|abcdefghijklmnop|')
    assert compare_ltiv_data(expect, actual), \
        'Did not pass second assertion. Expected {}. Got {}'.format(expect, actual)

    with pytest.raises(AssertionError):
        reports_fixture.parse_ltiv_data('3|NONE|Return|this|7|NONE|x|xxxxxxx|')

    expect = {'Return': ('this', 'NONE'), 'x': ('xxx|xxx', 'NONE')}
    actual = reports_fixture.parse_ltiv_data('4|NONE|Return|this|7|NONE|x|xxx|xxx|')
    assert compare_ltiv_data(expect, actual), \
        'Did not pass extra delimiter test. Expected {}. Got {}'.format(expect, actual)

    expect = {}
    actual = reports_fixture.parse_ltiv_data('')
    assert compare_ltiv_data(expect, actual), 'Empty case failed. Expected {}. Got {}'.format(expect, actual)

    expect = {'': ('', '')}
    actual = reports_fixture.parse_ltiv_data('0||||')
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
