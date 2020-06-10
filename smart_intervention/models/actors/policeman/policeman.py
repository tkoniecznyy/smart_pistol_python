from typing import Callable

from smart_intervention.globals import Notifications, CityMap
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.geolocation.location import Location
from smart_intervention.geolocation.map import RoutingError
from smart_intervention.models.actors.bases.purposeful_actor import PurposefulActor
from smart_intervention.models.actors.policeman.policeman_action import PolicemanAction
from smart_intervention.models.actors.policeman.policeman_notification import PolicemanNotification
from smart_intervention.models.actors.policeman.policeman_notification_processor import PolicemanNotificationProcessor
from smart_intervention.models.actors.policeman.policeman_purpose import PolicemanPurpose
import logging
log = logging.getLogger('PolicemanLogger')

class PolicemanError(Exception):
    pass


class Policeman(PurposefulActor, GeolocatedActor):
    """
    Actor which can be re-purposed by headquarters or simulation manager to dispatch it to assist other units
    Can dispatch messages to simulation manager for requesting of assistance in intervention
    Is geolocated and capable of moving around the map for fulfilling its current purpose
    """

    def __init__(self, purpose: PolicemanPurpose, location: Location, efficiency):
        super().__init__(purpose)
        super(PurposefulActor, self).__init__(location)
        self._last_purpose = purpose
        self.efficiency = efficiency

        self.current_route = None
        self.patrol_route = None
        self.intervention_event = None
        self.log = logging.getLogger(f'Policeman#{id(self)}')

    def re_purpose(self, purpose):
        self._store_purpose(purpose)
        log.info(f'Changing purpose to #{purpose.value}')
        super().re_purpose(purpose)

    def tick_action(self, notifications) -> Callable:
        def action():
            processable_notifications = notifications.get_notifications_for_processing(self)
            processable_notifications = processable_notifications.get()
            processable_notifications = [
                notification for notification in processable_notifications
                if notification.payload['policeman'] == self
            ]  # Filter out notifications for other instances of policemen
            log.debug(f'Received {len(processable_notifications)} processable notifications')
            PolicemanNotificationProcessor(self).process(processable_notifications)
            PolicemanAction(self).execute()

        return action

    def _store_purpose(self, purpose):
        arrived_at_intervention = purpose in [
            PolicemanPurpose.INTERVENTION,
            PolicemanPurpose.GUNFIGHT
        ] and self._last_purpose is PolicemanPurpose.ROUTING
        if not arrived_at_intervention:
            self._last_purpose = self.purpose
            self._last_location = self.location

    def _route_to(self, route):
        self.log.debug(f'Routing to {route}')  # TODO: Simplify
        self.current_route = route

    def route_with_purpose(self, location, purpose):
        self._route_to(CityMap.route(self.location, location))
        self.re_purpose(purpose)

    def try_join_event(self):
        intervention_event = self.location.intervention_event
        if intervention_event:
            self.intervention_event = intervention_event
            intervention_event.join(self)

            if intervention_event.armed_combat:
                self.re_purpose(PolicemanPurpose.GUNFIGHT)
            else:
                self.re_purpose(PolicemanPurpose.INTERVENTION)
        else:
            raise PolicemanError('No event in given location')

    def return_to_duty(self):
        self.log.info(f'Returning to duty')
        if self._last_purpose is PolicemanPurpose.PATROL:
            self.re_purpose(PolicemanPurpose.PATROL)
        elif self._last_purpose is PolicemanPurpose.IDLE:
            self._route_to(CityMap.route(self.location, self._last_location))
        self.send_notification(notification_type=PolicemanNotification.RETURNING_TO_DUTY)

    def move_and_join_event(self):
        try:
            self.move_forward(self.current_route)
        except RoutingError:
            self.try_join_event()

    def send_notification(self, notification_type, payload=None):
        self.log.debug(f'Sending notification {notification_type.value}, payload: {payload}')
        Notifications.send(
            actor=self,
            notification_type=notification_type,
            payload=payload
        )

    def send_notification_with_location(self, notification_type):
        self.send_notification(
            notification_type=notification_type, payload={'location': self.location}
        )
