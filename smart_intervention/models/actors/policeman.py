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
        PATROL = 'patrol'

    def __init__(self, purpose: PolicemanPurpose, location: Location):
        super().__init__(purpose)
        super(BaseActor, self).__init__(location)

    def tick_action(self, notifications) -> Callable:
        # TODO: Determine undertaken action on notifications in the system
        print(str(id(self)) + 'has received ' + notifications + ' nots in this tick')
        def action():
            print('My location is ', self._location.id)  # TODO: Remove

            {
                Policeman.PolicemanPurpose.IDLE: lambda: None,
                Policeman.PolicemanPurpose.PATROL: lambda: patrol_actions
            }[self.purpose]()

        return action



    def location(self) -> Location:
        return self._location

    def re_purpose(self, purpose: PolicemanPurpose):
        super().re_purpose(purpose)
