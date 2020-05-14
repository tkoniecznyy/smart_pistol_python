from smart_intervention import Location
from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.models.actors.bases.purpose import PassiveActorPurpose


class Drone(BaseActor, GeolocatedActor):
    """
    A geolocated actor, placed on alternative map
    This has its own navigation, and like any other actor can be managed and re-purposed
    """

    class DronePurpose(PassiveActorPurpose):
        IN_FLIGHT = 'in_flight'

    def __init__(self, purpose: DronePurpose, location: Location):
        super().__init__(purpose)
        super(BaseActor, self).__init__(location)
