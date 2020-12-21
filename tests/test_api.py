"""Test suite for src.api"""
from datetime import date, datetime, timedelta
import logging
import random


def get_random_route(rs_api) -> int:
    """Gets a random route id used for testing"""
    routes = rs_api.get_routes()
    index = random.randint(1, len(routes) - 1)
    route_id = routes[index]['RouteID']
    logging.getLogger().info("Selecting RouteID %s", route_id)
    return route_id


def test_api_get_routes_for_map_with_schedule_with_encoded_line(ridesystems_api):
    """Test for Ridesystems API method get_routes_for_map_with_schedule_with_encoded_line"""
    ret = ridesystems_api.get_routes_for_map_with_schedule_with_encoded_line()
    assert isinstance(ret, list)
    assert ret


def test_api_get_map_vehicle_points(ridesystems_api):
    """Test for Ridesystems API method get_map_vehicle_points"""
    ret = ridesystems_api.get_map_vehicle_points()
    assert isinstance(ret, list)
    assert ret


def test_api_get_vehicle_route_stop_estimates(ridesystems_api):
    """Test for Ridesystems API method get_vehicle_route_stop_estimates"""
    ret = ridesystems_api.get_vehicle_route_stop_estimates([get_random_route(ridesystems_api)])
    assert isinstance(ret, list)
    assert ret


def test_api_get_stop_arrival_times(ridesystems_api):
    """Test for Ridesystems API method get_stop_arrival_times"""
    ret = ridesystems_api.get_stop_arrival_times()
    assert isinstance(ret, list)
    assert ret


def test_api_get_route_stop_arrivals(ridesystems_api):
    """Test for Ridesystems API method get_route_stop_arrivals"""
    ret = ridesystems_api.get_route_stop_arrivals()
    assert isinstance(ret, list)
    assert ret


def test_api_get_route_schedules(ridesystems_api):
    """
    Test for Ridesystems API method get_route_schedules. Ride systems doesn't support this, so we don't check for data.
    """
    ret = ridesystems_api.get_route_schedules([get_random_route(ridesystems_api)])
    assert isinstance(ret, list)
    assert len(ret) >= 0  #


def test_api_get_route_schedule_times(ridesystems_api):
    """
    Test for Ridesystems API method get_route_schedule_times. Ride systems doesn't support this, so we don't check for
    data
    """
    ret = ridesystems_api.get_route_schedule_times()
    assert isinstance(ret, list)
    assert len(ret) >= 0  # Ride systems doesn't support this


def test_api_get_routes(ridesystems_api):
    """Test for Ridesystems API method get_routes"""
    ret = ridesystems_api.get_routes()
    assert isinstance(ret, list)
    assert ret


def test_api_get_stops(ridesystems_api):
    """Test for Ridesystems API method get_stops"""
    ret = ridesystems_api.get_stops()
    assert isinstance(ret, list)
    assert ret


def test_api_get_markers(ridesystems_api):
    """Test for Ridesystems API method get_markers. Ride systems doesn't support this, so we don't check for data."""
    ret = ridesystems_api.get_markers([get_random_route(ridesystems_api)])
    assert isinstance(ret, list)
    assert len(ret) >= 0  # Ridesystems doesn't provide this


def test_api_get_map_config(ridesystems_api):
    """Test for Ridesystems API method get_map_config"""
    ret = ridesystems_api.get_map_config()
    assert isinstance(ret, dict)
    assert ret


def test_api_get_routes_for_map(ridesystems_api):
    """Test for Ridesystems API method get_routes_for_map"""
    ret = ridesystems_api.get_routes_for_map()
    assert isinstance(ret, list)
    assert ret


def test_api_get_ridership_data(ridesystems_api):
    """
    Test for Ridesystems API method get_ridership_data. Ridesystems doesn't have ridership data, so we don't check for
    data
    """
    ret = ridesystems_api.get_ridership_data(date.today(), date.today())
    assert isinstance(ret, list)

    yesterday = datetime.now() - timedelta(days=1)
    ret = ridesystems_api.get_ridership_data(datetime.now(), yesterday)
    assert isinstance(ret, list)
