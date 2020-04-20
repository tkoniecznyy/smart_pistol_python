from typing import List

from networkx import Graph

from .location import Location
from .geolocated_actor import GeolocatedActor


class Map:
    """
    Class which is responsible for location of the actors and managing its graph
    """
    def __init__(self, actors: List[GeolocatedActor], graph: Graph):
        # TODO: Adding actors to the graph at set location + validation
        pass

    def find_nearest_actor(self, location: Location, actor_class):
        pass

    def route(self, a: Location, b: Location):
        pass

    def place_actor_at(self, actor, location: Location):
        pass