from abc import ABC
from typing import List
from smart_intervention.globals import CityMap
from smart_intervention.geolocation.map import RoutingError


class GeolocatedActor(ABC):
    """
    Actor which must provide its location on call
    """

    def __init__(self, location):
        self.location = location
        location.add_actor(self)

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
            self.move_to(first_waypoint)
        else:
            route_to_waypoint = CityMap.route(self.location, first_waypoint)
            try:
                self.move_to(route_to_waypoint[0])
            except IndexError:
                raise RoutingError('Cannot find route to waypoint')
        if hasattr(self, 'log'):
            self.log.info(f'Moving to {id(first_waypoint)}')

    def move_to(self, location):
        self.declare_move()
        self.location.remove_actor(self)
        self.location = location
        self.location.add_actor(self)

    def declare_move(self):
        CityMap.declare_move()

        actor_class = self.__class__.__name__
        if actor_class == 'Policeman':
            CityMap.declare_policeman_move()
        elif actor_class == 'Ambulance':
            CityMap.declare_ambulance_move()
        else:
            raise RuntimeError('Did not recognise geo actor class')
