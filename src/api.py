""""
The Ridesystems API, to access workable data of any Ridesystems system
Written by: Ritwik Gupta (2015)
Updated by: Brian Seel (2020) brian.seel@baltimorecity.gov

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from typing import Dict, Any, Optional, TypedDict, Union, List
from datetime import datetime, date

from tenacity import retry, wait_random_exponential, stop_after_attempt
import requests

# Note: We disable unsubscriptable-object because of bug bug: https://github.com/PyCQA/pylint/issues/3882 in pylint.
# When that is fixed, we can remove the disables


# Return types used for type checking
class StopArrivalTimesDict(TypedDict):  # pylint:disable=too-few-public-methods,inherit-non-class
    """Used for type checking"""
    timesPerStop: int
    routeIDs: Optional[str]  # pylint:disable=unsubscriptable-object
    routeStopIDs: Optional[str]  # pylint:disable=unsubscriptable-object
    ApiKey: Optional[str]  # pylint:disable=unsubscriptable-object


class VehicleRouteStopEstimates(TypedDict):  # pylint:disable=too-few-public-methods,inherit-non-class
    """Used for type checking"""
    quantity: str
    vehicleIdStrings: Optional[str]  # pylint:disable=unsubscriptable-object
    ApiKey: Optional[str]  # pylint:disable=unsubscriptable-object


class RouteSchedules(TypedDict):  # pylint:disable=too-few-public-methods,inherit-non-class
    """Used for type checking"""
    routeID: Optional[int]  # pylint:disable=unsubscriptable-object
    ApiKey: Optional[str]  # pylint:disable=unsubscriptable-object


RidershipDate = Union[date, datetime]  # pylint:disable=unsubscriptable-object


class Ridership(TypedDict):  # pylint:disable=too-few-public-methods,inherit-non-class
    """Used for type checking"""
    StartDate: RidershipDate
    EndDate: RidershipDate
    ApiKey: Optional[str]  # pylint:disable=unsubscriptable-object


ApiDataTypes = Union[VehicleRouteStopEstimates, StopArrivalTimesDict, RouteSchedules, Ridership]  # pylint:disable=unsubscriptable-object
QueryResult = Dict[str, Any]
QueryResultList = List[QueryResult]


class API:
    """Wrapper for the Ride Systems API. Their API is pretty terrible, so a lot of functionality is in the scraper from
    ridesystems.reports.Reports"""

    def __init__(self, api_key: str, base_url="https://cityofbaltimore.ridesystems.net"):
        """
        :param api_key: Ridesystems API key (although nothing really happens if you don't provide one. RS doesn't check)
        :param base_url: Base url of your Ride Systems instance
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.session()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_routes_for_map_with_schedule_with_encoded_line(self) -> QueryResultList:
        """
        Used to retrieve active Routes from Ride Systems. Also contains a link to a schedule for each particular route

        :return RouteWithSchedule: List of dictionaries with the following information
            RouteID – Unique identifier for the route
            Description – Description of the route
            TextingKey – Unique string that represents the route when texted to Ride Systems
            MapLineColor – Color of the route on the map
            MapZoom – Default zoom level to set when this route is selected
            MapLatitude – Default latitude to set when this route is selected
            MapLongitude – Default longitude to set when this route is selected
            IsVisibleOnMap – Reflects whether this route should be shown on the main page
            IsCheckedOnMap –Reflects whether this route should be checked by default on the main page
            IsCheckLineOnlyOnMap– Does not show on app
            Order – Where this route falls in order with the other routes
            StopTimesPDFLink – Link to use to get the schedule for this route
            HideRouteLine – Setting on whether to show the route line
            ShowPolygon– Setting to show the route line as a polygon rather than a line
            InfoText– Subline text to use in the map panel for this route
            EncodedPolyline – Google encoded points that make up the polyline
            ETATypeID – What times do we show for the stops: 1) Estimates, 2) Schedules, or 3) SchedulesWithEstimates?
                        1. Estimates – Show the Estimate time (in time of day or minutes to arrival based on
                            EstimateDisplayType)
                        2. Schedules – Show the Scheduled time (in time of day or minutes to arrival based on
                            EstimateDisplayType)
                        3. Schedule With Estimates – Show the later of either the Schedule Time or Estimate time (in
                            time of day or minutes to arrival based on EstimateDisplayType)
            ShowRouteArrows– Setting on whether to show arrows on the Route Line
            UseScheduleTripsInPassengerCounter– Not used
            VehicleMarkerCssClass– CSS Class for Vehicle Marker
            Stops - Name of the stop
            RouteStopID– Unique Identifier for a Stop on a Route
            RouteID – Unique Identifier for a Route
            RouteDescription – Description of the Route
            Description – Description of the Stop
            Order – Order of this stop in comparison with the other stops.
            Heading – GPS Heading taken when the bus moves away from this stop.
            SecondsAtStop – Number of seconds the bus stays at this stop before moving to the next
            SecondsToNextStop – Number of seconds it takes the bus from move from this stop to the next.
            ShowEstimatesOnMap – Reflects setting on whether to show the estimates for this stop on the mapcpanel
            ShowDefaultedOnMap –Reflects whether to show this stop on the map
            TextingKey – Unique string that represents the Stop when texted to Ride Systems
            MaxZoomLevel –Reflects the zoom level to start showing this stop to the user
            SignVerbiage– Alternate Stop Description used by Sign Applications
            MapPoints– Not used
            Landmarks – Misc landmarks associated with this particular route
            LandmarkID – Unique identifier for the Landmark
            Label – Description to be put on the map
            AddressID – Unique ID associated with the address of this Landmark
            Latitude
            Longitude
        """
        response = self.session.get(
            "{}/Services/JSONPRelay.svc/GetRoutesForMapWithScheduleWithEncodedLine".format(self.base_url))
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_map_vehicle_points(self) -> QueryResultList:
        """
        Return the map location for all active vehicles.

        :return vehicle: (list) List of dictionaries containing the following information
            VehicleID — Unique Identifier for a Vehicle
            RouteID – Unique Identifier for a Route
            Name – Name of the Vehicle
            Latitude – Latitude of Vehicle’s current position
            Longitude – Longitude of Vehicle’s current position
            GroundSpeed – Speed of Vehicle
            Heading – Heading of Vehicle
            Seconds – Seconds since the vehicle reported its location
            IsOnRoute – Is the vehicle on Route?
            IsDelayed– Is the vehicle Delayed?
        """
        response = self.session.get("{}/Services/JSONPRelay.svc/GetMapVehiclePoints".format(self.base_url))
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_vehicle_route_stop_estimates(self, vehicle_id: List[int],
                                         quantity: int = 2) -> QueryResultList:
        """Return {quantity} stop estimates for all active vehicles.

        :param vehicle_id: (list) List of integers of Vehicle ID’s to retrieve
        :param quantity: (int) Number of records to return.

        :return vehicleestimates: The following information
            VehicleID — Unique Identifier for a Vehicle
            Estimates[] – Estimates
            RouteStopId – Unique ID of each Route Stop
            Description – Description of Route Stop
            OnRoute – Is the vehicle on Route?
            VehicleId – ID of Vehicle
            Text – Text of Estimate
            Time –Time of Day of expected arrival
            Seconds – Estimated Seconds until Arrival
            IsArriving – Is the vehicle arriving?
            EstimateTime – Estimated arrival Time of Day
            ScheduledTime – Scheduled arrival Time of Day
            OnTimeStatus– 0 – On time, 2 – Early, 3 – Late

        """
        payload: VehicleRouteStopEstimates = {"quantity": str(quantity),
                                              "vehicleIdStrings": None,
                                              "ApiKey": self.api_key}

        if vehicle_id:
            payload["vehicleIdStrings"] = ",".join(str(i) for i in vehicle_id)
        response = self.session.get("{}/Services/JSONPRelay.svc/GetVehicleRouteStopEstimates".format(self.base_url),
                                    params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_stop_arrival_times(self, times_per_stop: int = 1,
                               route_ids: List[int] = None,
                               stop_ids: List[int] = None) -> QueryResultList:
        """
        Return stop arrival times for all vehicles.

        :param times_per_stop: (int) Optional, number of scheduled times to return.
        :param route_ids: (list) Optional, to restrict the results to given Route ID(s).
        :param stop_ids: (list of ints) Optional, to restrict the results to given Stop ID(s)

        :return RouteStopArrival: (List of dictionaries) the following information
            RouteID – Unique Identifier for a Route
            RouteStopID – Unique identifier for a Route Stop
            Description – Not used
            Times[] – Arrival Times
            VehicleId – ID of Vehicle
            Text – Text of Estimate
            Time – Time of Day of expected arrival
            Seconds – Estimated Seconds till Arrival
            IsArriving – Is the vehicle arriving?
            EstimateTime – Estimated arrival Time of Day
            ScheduledTime – Scheduled arrival or departure Time of Day
            IsDeparted – Has the vehicle departed?
            ScheduledArrivalTime – Scheduled arrival Time of Day
            ScheduledDepartureTime – Scheduled departure Time of Day
            OnTimeStatus– 0 – On time, 2 – Early, 3 – Late
        """
        payload: StopArrivalTimesDict = {"timesPerStop": times_per_stop,
                                         "routeIDs": None,
                                         "routeStopIDs": None,
                                         "ApiKey": self.api_key}
        if route_ids:
            payload["routeIDs"] = ", ".join([str(x) for x in route_ids])

        if stop_ids:
            payload["routeStopIDs"] = ", ".join(map(str, stop_ids))

        response = self.session.get("{}/Services/JSONPRelay.svc/GetStopArrivalTimes".format(self.base_url),
                                    params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_route_stop_arrivals(self, times_per_stop: int = 1) -> QueryResultList:
        """
        Return stop arrival times for all vehicles.
        :param times_per_stop: (int) Optional, number of scheduled times to return.

        :return:
            RouteID - value representing the route
            RouteStopID - value representing the stop
            ScheduledTimes - dictionary with the following values for the RouteStopID
                ArrivalTimeUTC - scheduled arrival tim->e
                AssignedVehicleId - VehicleID assigned to the block with this scheduled arrival
                Block - string identifying the block assigned to the next arrival
                DepartureTimeUTC - scheduled stop departure time
            VehicleEstimates - dictionary with the following values for each VehicleID
                Block - string identifying the schedule block
                OnRoute - is the vehicle on the assigned route
                SecondsToStop - seconds until we get to RouteStopID
                VehicleId – ID of Vehicle
        """

        payload: StopArrivalTimesDict = {"timesPerStop": times_per_stop,
                                         "routeIDs": None,
                                         "routeStopIDs": None,
                                         "ApiKey": self.api_key}
        response = self.session.get("{}/Services/JSONPRelay.svc/GetRouteStopArrivals".format(self.base_url),
                                    params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_route_schedules(self, route_id: int = None) -> QueryResultList:
        """
        Used to return scheduled times for a Route. This is used for cyclical routes, where the route runs twice an
        hour on the exact same path and schedule.

        :param route_id: (int) Optional, to restrict the results to a given Route ID

        :return RouteSchedule: (list of dictionaries)
            RouteScheduleID – Unique ID for each schedule
            RouteID – Unique Identifier for a Route
            StartTime – Time of day the Route Schedule starts
            StartTimeUTC – UTC Time of day the Route Schedule starts
            EndTime – Time of day the Route Schedule ends
            EndTimeUTC – UTC Time of day the Route Schedule ends
            LoopsPerHour – Number of loops run per hour
            StopTimes -
            RouteStopScheduleID – Unique ID for each stop on the schedule
            RouteScheduleID – Unique ID for the schedule
            RouteStopID – Unique Identifier for a Stop on a Route
            MinutesAfterStart – Number of minutes after the start of the loop until arrival at this stop
        """
        payload: RouteSchedules = {"routeID": route_id, "ApiKey": self.api_key}
        response = self.session.get("{}/Services/JSONPRelay.svc/GetRouteSchedules".format(self.base_url),
                                    params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_route_schedule_times(self, route_id: int = None) -> QueryResultList:
        """
        Used to return times in the day that a Route is active.

        :param route_id: (int) Optional, to restrict the results to a given Route ID.

        :return RouteScheduleTime: (list of dictionaries)
            RouteID – Unique Identifier for a Route
            StartTimeUTC – UTC time of day the Route Schedule starts
            EndTimeUTC – UTC time of day the Route Schedule ends
            StartTime – Time of day (in MST) the Route Schedule starts
            EndTime – Time of day (in MST) the Route Schedule ends
            ServerTime– Current time of day (in MST)
            ServerTimeUTC– UTC Current Time of day
        """
        payload: RouteSchedules = {"routeID": route_id, "ApiKey": self.api_key}
        response = self.session.get("{}/Services/JSONPRelay.svc/GetRouteScheduleTimes".format(self.base_url),
                                    params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_routes(self, route_id: int = None) -> QueryResultList:
        """
        Abbreviated view of all active Routes on Ride Systems. Used for Smart Phones where data size is a limiting
        factor.

        :param route_id: (int) Optional, to restrict the results to a given Route ID.

        :return SmartPhoneRoute: (list of dictionaries)
            RouteID – Unique Identifier for a Route
            Description – Description of the Route
            MapLineColor – Color of the Route on the Map
            MapZoom – Default Zoom level to set when this route is selected
            MapLatitude – Default Latitude to set when this route is selected
            MapLongitude – Default Longitude to set when this route is selected
            IsVisibleOnMap – Reflects if this route should be shown on the main page
            StopTimesPDFLink – Link to use to get the Schedule for this Route
            HideRouteLine – Setting on whether to show the Route Line
            UseScheduleTripsInPassengerCounter– Not used
        """
        payload: RouteSchedules = {"routeID": route_id, "ApiKey": self.api_key}
        response = self.session.get("{}/Services/JSONPRelay.svc/GetRoutes".format(self.base_url), params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_stops(self, route_id: int = None) -> QueryResultList:
        """
        Abbreviated view of all active Stops on a route. Used for Smart Phones where data size is a limiting factor.

        :param route_id: (int) Optional, to restrict the results to a given Route ID.

        :return SmartPhoneRouteStop: (list of dictionaries)
            RouteStopID – Unique Identifier for a Stop on a Route
            RouteID – Unique Identifier for a Route
            Description – Description of the Stop
            Longitude
            Latitude
            TextingKey – Unique string that represents the Stop when Texted to Ride Systems
            MaxZoomLevel –Reflects the zoom level to start showing this stop to the user
            ShowEstimatesOnMap – Reflects setting on whether to show the estimates for this stop on the map
            panel
            ShowDefaultedOnMap – Reflects whether to show this stop on the map
            MapPoints – GPS points that make up the path to the next stop
            Latitude
            Longitude
            Heading- Not used
        """
        payload: RouteSchedules = {"routeID": route_id, "ApiKey": self.api_key}
        response = self.session.get("{}/Services/JSONPRelay.svc/GetStops".format(self.base_url), params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_markers(self, route_id: int = None) -> QueryResultList:
        """
        Abbreviated view of all active Landmarks on a route. Used for Smart Phones where data size is a limiting factor.

        :param route_id: (int) Optional, to restrict the results to a given Route ID.

        :return SmartPhoneLandmark: (list of dictionaries)
            RouteID – Unique Identifier for a Route
            LandmarkID – Unique identifier for the Landmark
            Label – Description to be put on the map
            Latitude
            Longitude
        """
        payload: RouteSchedules = {"routeID": route_id, "ApiKey": self.api_key}
        response = self.session.get("{}/Services/JSONPRelay.svc/GetMarkers".format(self.base_url),
                                    params=payload)
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_map_config(self) -> QueryResult:
        """
        Returns settings that are used for laying out the map

        :return MapConfig: See docs for return information
        """
        response = self.session.get("{}/Services/JSONPRelay.svc/GetMapConfig".format(self.base_url))
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_routes_for_map(self) -> QueryResultList:
        """Return the routes with Vehicle Route Name, Vehicle ID, and all stops, etc."""
        response = self.session.get("{}/Services/JSONPRelay.svc/GetRoutesForMap".format(self.base_url))
        return response.json()

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(7), reraise=True)
    def get_ridership_data(self, start_date: RidershipDate,
                           end_date: RidershipDate) -> QueryResultList:
        """
        Return the ridership from an APC

        :param start_date: The date to begin the range (either in the format 2020-03-01 or 2020-03-01 1:00 PM)
        :type start_date: str
        :param end_date: The date to end the range (same format as start_date)
        :type end_date: str

        :return Ridership: (list of dictionaries)
            ClientTime
            Counter
            CounterType
            Entries
            Exits
            Latitude
            LongBadgeNumber
            Longitude
            Route
            RouteID
            RouteStop
            RouteStoopID
            ShortBadgeNumberUTC
            Time
            Vehicle
            VehicleID
        """
        payload: Ridership = {"StartDate": start_date, "EndDate": end_date, "ApiKey": self.api_key}
        response = self.session.get("{}/Services/JSONPRelay.svc/GetRidershipData".format(self.base_url),
                                    params=payload)
        return response.json()


