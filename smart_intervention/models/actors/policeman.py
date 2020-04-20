from typing import Callable

from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.geolocation.location import Location

from smart_intervention.models.actors.bases.purpose import Purpose


class Policeman(BaseActor, GeolocatedActor):
    """
    Actor which can be re-purposed by headquarters or simulation manager to dispatch it to assist other units
    Can dispatch messages to simulation manager for requesting of assistance in intervention
    Is geolocated and capable of moving around the map for fulfilling its current purpose
    """

    class PolicemanPurpose(Purpose):
        """
        Class for keeping policeman purposes
        """
        IDLE = 'idle'

    def __init__(self, purpose: PolicemanPurpose, location: Location):
        super().__init__(purpose)
        super(BaseActor, self).__init__(location)

    def tick_action(self) -> Callable:
        def action():
            print('My location is ', self._location)  # TODO: Remove

        return action

    def location(self) -> Location:
        return self._location

    def re_purpose(self, purpose: PolicemanPurpose):
        super().re_purpose(purpose)
