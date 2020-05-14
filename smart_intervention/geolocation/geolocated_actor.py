from abc import ABC, abstractmethod
from typing import List
from smart_intervention import CityMap
from smart_intervention.geolocation.map import RoutingError

class GeolocatedActor(ABC):
    """
    Actor which must provide its location on call
    """

    def __init__(self, location):
        self.location = location

    def move_forward(self, route: List):
        """
        Method which moves the actor towards end of the route
        If actor is not on an edge adjacent to beginning of the route, it routes him towards the beginning,
        with most optimal route
        :return:
        """
        try:
            first_waypoint = route.pop(0)
        except IndexError:
            raise RoutingError('Cannot move forward, empty route')

        if CityMap.are_neighbors(first_waypoint, self.location):
            self.location = first_waypoint
        else:
            route_to_waypoint = CityMap.route(self.location, first_waypoint)
            try:
                self.location = route_to_waypoint[0]
            except IndexError:
                raise RoutingError('Cannot find route to waypoint')
