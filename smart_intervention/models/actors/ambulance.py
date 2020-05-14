from smart_intervention import Location
from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.models.actors.bases.purpose import Purpose


class Ambulance(BaseActor, GeolocatedActor):
    """
    Actor managed exclusively by headquarters
    Can be re-purposed to change its stationing location or dispatch it to action
    """

    class AmbulancePurpose(Purpose):
        IDLE = 'idle'
        ENROUTE_ASSISTANCE = 'enroute_assistance'

    def __init__(self, purpose: AmbulancePurpose, location: Location):
        super().__init__(purpose)
        super(BaseActor, self).__init__(location)
