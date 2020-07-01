import logging
from enum import Enum
from typing import Callable

from smart_intervention.geolocation.location import Location
from smart_intervention.globals import Notifications, CityMap
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.geolocation.map import RoutingError
from smart_intervention.models.actors.ambulance.ambulance_notification import AmbulanceNotification
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import \
    AmbulanceHeadquarterNotification
from smart_intervention.models.actors.bases.purposeful_actor import PurposefulActor
from smart_intervention.utils.processing import mass_process


class AmbulanceError(Exception):
    pass


class Ambulance(PurposefulActor, GeolocatedActor):
    class AmbulancePurpose(Enum):
        IDLE = 'idle'
        ROUTING_TO_ASSIST = 'routing_to_assist'
        ASSISTING = 'assisting'
        ROUTING_TO_HQ = 'routing_to_hq'

    def __init__(self, purpose: AmbulancePurpose, location: Location, efficiency, ambulance_hq: Location):
        super().__init__(purpose)
        super(PurposefulActor, self).__init__(location)
        self.efficiency = efficiency
        self.intervention_event = None
        self.ambulance_hq = ambulance_hq
        self.current_route = None
        self.log = logging.getLogger(f'Ambulance#{id(self)}')

    def tick_action(self, notifications) -> Callable:
        def action():
            processable_notifications = notifications.get_notifications_for_processing(self)
            processable_notifications = processable_notifications.get()
            processable_notifications = [
                notification for notification in processable_notifications
                if notification.payload['ambulance'] == self
            ]  # Filter out notifications for other instances of ambulances
            self.log.debug(f'Received {len(processable_notifications)} processable notifications')
            self._process_notifications(processable_notifications)
            self._take_action()

        return action

    def re_purpose(self, purpose):
        self.log.info(f'Changing purpose to #{purpose.value}')
        super().re_purpose(purpose)

    def _route_to(self, route):
        self.log.debug(f'Routing to {route[-1]}')
        self.current_route = route

    def _route_with_purpose(self, location, purpose):  # TODO: Refactor - abstract out to geolocated + purposeful actor
        self._route_to(CityMap.route(self.location, location))
        self.re_purpose(purpose)

    @mass_process
    def _process_notifications(self, notifications):
        def process_one(notification):
            if notification.type == AmbulanceHeadquarterNotification.DISPATCH_TO_EVENT:
                event_location = notification.payload['location']
                self._route_with_purpose(event_location, Ambulance.AmbulancePurpose.ROUTING_TO_ASSIST)

        return notifications, process_one

    def _take_action(self):
        {
            Ambulance.AmbulancePurpose.IDLE: lambda: None,
            Ambulance.AmbulancePurpose.ROUTING_TO_ASSIST: self._routing_actions,
            Ambulance.AmbulancePurpose.ASSISTING: self._assisting_actions,
            Ambulance.AmbulancePurpose.ROUTING_TO_HQ: self._routing_actions,
        }[self.purpose]()

    def move_and_join_event(self):
        try:
            self.move_forward(self.current_route)
        except RoutingError:
            self.try_join_event()

    def try_join_event(self):
        intervention_event = self.location.intervention_event
        if intervention_event:
            self.intervention_event = intervention_event
            intervention_event.join(self)
            self.re_purpose(Ambulance.AmbulancePurpose.ASSISTING)
            self.log.info(f'Joined intervention event {id(intervention_event)} to assist')
        else:
            raise AmbulanceError('No event in given location')

    def _routing_actions(self):
        try:
            self.move_and_join_event()
        except AmbulanceError as a_err:  # This piece is used like a safeguard for routing to hq
            if self.purpose is Ambulance.AmbulancePurpose.ROUTING_TO_HQ:
                self.re_purpose(Ambulance.AmbulancePurpose.IDLE)
            else:
                raise a_err

    def _assisting_actions(self):
        if self.intervention_event.active:  # If the actions grow, make a similar inactive guard as in policeman
            self.send_notification_with_location(AmbulanceNotification.ASSISTING)
            self.intervention_event.mitigate(self)
        else:
            self._route_with_purpose(self.ambulance_hq, AmbulanceNotification.RETURNING_TO_HQ)
            self.send_notification(AmbulanceNotification.RETURNING_TO_HQ)

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
