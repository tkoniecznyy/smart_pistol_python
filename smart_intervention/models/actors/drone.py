from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor


class Drone(BaseActor, GeolocatedActor):
    """
    A geolocated actor, placed on alternative map
    This has its own navigation, and like any other actor can be managed and re-purposed
    """