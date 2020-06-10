from typing import Callable

from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.geolocation.location import Location
from smart_intervention.models.actors.bases.purposeful_actor import PurposefulActor


class Drone(PurposefulActor, GeolocatedActor):
    """
    A geolocated actor, placed on alternative map
    This has its own navigation, and like any other actor can be managed and re-purposed
    """

    def tick_action(self, notifications) -> Callable:
        raise NotImplementedError  # TODO: Implement

    def re_purpose(self, purpose):
        raise NotImplementedError  # TODO: Implement

    class DronePurpose:
        IDLE = 'idle'
        IN_FLIGHT = 'in_flight'

    def __init__(self, purpose: DronePurpose, location: Location):
        super().__init__(purpose)
        super(PurposefulActor, self).__init__(location)
