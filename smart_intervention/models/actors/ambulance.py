from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor


class Ambulance(BaseActor, GeolocatedActor):
    """
    Actor managed exclusively by headquarters
    Can be re-purposed to change its stationing location or dispatch it to action
    """
    pass
