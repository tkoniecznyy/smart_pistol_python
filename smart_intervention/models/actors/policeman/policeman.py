from typing import Callable

from smart_intervention import CityMap, Notifications
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.geolocation.location import Location
from smart_intervention.models.actors.bases.purpose import PassiveActorPurpose
from smart_intervention.models.actors.bases.purposeful_actor import PurposefulActor
from smart_intervention.models.actors.policeman.policeman_action import PolicemanAction
from smart_intervention.models.actors.policeman.policeman_notification_processor import PolicemanNotificationProcessor
from smart_intervention.notifications.notification_store import NotificationType


class PolicemanError(Exception):
    pass


class Policeman(PurposefulActor, GeolocatedActor):
    """
    Actor which can be re-purposed by headquarters or simulation manager to dispatch it to assist other units
    Can dispatch messages to simulation manager for requesting of assistance in intervention
    Is geolocated and capable of moving around the map for fulfilling its current purpose
    """

    class PolicemanNotification(NotificationType):
        BACKUP_NEEDED = 'backup_needed'
        IN_COMBAT = 'in_combat'

    class PolicemanPurpose(PassiveActorPurpose):
        """
        Class for keeping policeman purposes
        """
        PATROL = 'patrol'
        INTERVENTION = 'intervention'
        GUNFIGHT = 'gunfight'
        ROUTING_TO_INTERVENTION = 'routing_to_intervention'
        ROUTING_TO_GUNFIGHT = 'routing_to_combat'

    def __init__(self, purpose: PolicemanPurpose, location: Location, success_rate):
        super().__init__(purpose)
        super(PurposefulActor, self).__init__(location)
        self._last_purpose = purpose
        self.success_rate = success_rate

        self._current_route = None
        self._patrol_route = None
        self._intervention_event = None

    def re_purpose(self, purpose):
        self._store_purpose(purpose)
        super().re_purpose(purpose)

    def tick_action(self, notifications) -> Callable:
        def action():
            PolicemanNotificationProcessor(self).process(notifications)
            PolicemanAction(self).execute()

        return action

    def _store_purpose(self, purpose):
        arrived_at_intervention = purpose in [
            Policeman.PolicemanPurpose.INTERVENTION,
            Policeman.PolicemanPurpose.GUNFIGHT
        ] and self._last_purpose is Policeman.PolicemanPurpose.ROUTING
        if not arrived_at_intervention:
            self._last_purpose = self.purpose
            self._last_location = self.location

    def _route_to(self, route):
        self._current_route = route

    def _route_with_purpose(self, location, purpose):
        self._route_to(CityMap.route(self.location, location))
        self.re_purpose(purpose)

    def _try_join_event(self):  # TODO: Insert random intervention events to locations in sim manager
        intervention_event = self.location.get_intervention_event()
        if intervention_event:
            self._intervention_event = intervention_event
            intervention_event.join(self)

            if intervention_event.armed_combat:
                self.re_purpose(Policeman.PolicemanPurpose.GUNFIGHT)
            else:
                self.re_purpose(Policeman.PolicemanPurpose.INTERVENTION)

    def _return_to_duty(self):
        if self._last_purpose is Policeman.PolicemanPurpose.PATROL:
            self.re_purpose(Policeman.PolicemanPurpose.PATROL)
        elif self._last_purpose is Policeman.PolicemanPurpose.IDLE:
            self._route_to(CityMap.route(self.location, self._last_location))

    def _send_notification_with_location(self, notification_type):
        Notifications.send(
            actor=self,
            notification_type=notification_type,
            payload={'location': self.location},
        )
