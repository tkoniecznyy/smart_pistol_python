from typing import Callable

from smart_intervention import Location
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.models.actors.bases.purpose import AssistingActorPurpose, Purpose
from smart_intervention.models.actors.bases.purposeful_actor import PurposefulActor


class Ambulance(PurposefulActor, GeolocatedActor):
    """
    Actor managed exclusively by headquarters
    Can be re-purposed to change its stationing location or dispatch it to action
    """

    def re_purpose(self, purpose: Purpose):
        raise NotImplementedError  # TODO: Implement

    def tick_action(self, notifications) -> Callable:
        raise NotImplementedError  # TODO: Implement

    class AmbulancePurpose(AssistingActorPurpose):
        pass

    def __init__(self, purpose: AmbulancePurpose, location: Location):
        super().__init__(purpose)
        super(PurposefulActor, self).__init__(location)
