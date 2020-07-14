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


class PolicemanError(Exception):
    pass


class Policeman(PurposefulActor, GeolocatedActor):
    """
    Actor which can be re-purposed by headquarters or simulation manager to dispatch it to assist other units
    Can dispatch messages to simulation manager for requesting of assistance in intervention
    Is geolocated and capable of moving around the map for fulfilling its current purpose
    """

    def __init__(self, purpose: PolicemanPurpose, location: Location, efficiency, policeman_hq):
        super().__init__(purpose)
        super(PurposefulActor, self).__init__(location)
        self._last_purpose = purpose
        self.efficiency = efficiency
        self.policeman_hq = policeman_hq

        self.current_route = None
        self.patrol_route = None
        self.intervention_event = None
        self.log = logging.getLogger(f'Policeman#{id(self)}')

    def re_purpose(self, purpose):
        self._store_duty_purpose()
        self.log.info(f'Changing purpose to #{purpose.value}')
        super().re_purpose(purpose)

    def tick_action(self, notifications) -> Callable:
        def action():
            processable_notifications = notifications.get_notifications_for_processing(self)
            processable_notifications = [
                notification for notification in processable_notifications.get()
                if notification.payload['policeman'] == self
            ]  # Filter out notifications for other instances of policemen
            processable_number = len(processable_notifications)
            self.log.debug(f'Received {processable_number} processable notifications')
            Notifications.declare_received(processable_number)
            PolicemanNotificationProcessor(self).process(processable_notifications)
            PolicemanAction(self).execute()

        return action

    def _store_duty_purpose(self):
        if self.purpose in [PolicemanPurpose.IDLE, PolicemanPurpose.PATROL]:
            self._last_purpose = self.purpose

    def _route_to(self, route):
        self.log.debug(f'Routing to {id(route[-1])}')
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
            self.route_with_purpose(self.policeman_hq, PolicemanPurpose.RETURNING_TO_HQ)
        self.send_notification(notification_type=PolicemanNotification.RETURNING_TO_DUTY)

    def move_and_join_event(self):
        try:
            self.move_forward(self.current_route)
        except RoutingError:
            self.try_join_event()

    def send_notification(self, notification_type, payload=None):
        self.log.debug(f'Sending notification {notification_type.value}, payload: {payload}')
        Notifications.send(
            type=notification_type,
            actor=self,
            payload=payload
        )

    def send_notification_with_location(self, notification_type):
        self.send_notification(
            notification_type=notification_type, payload={'location': self.location}
        )

    def is_free(self):
        return self.purpose in [PolicemanPurpose.IDLE, PolicemanPurpose.PATROL]
