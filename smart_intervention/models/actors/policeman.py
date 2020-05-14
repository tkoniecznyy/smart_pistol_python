from typing import Callable

from smart_intervention import CityMap, Notifications
from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.geolocation.geolocated_actor import GeolocatedActor
from smart_intervention.geolocation.location import Location
from collections import defaultdict
from smart_intervention.models.actors.bases.purpose import ActiveActorPurpose
from smart_intervention.notifications.notification_store import NotificationType


class PolicemanError(Exception):
    pass


def return_to_duty_if_inactive(callback):
    def decorated(self, *args, **kwargs):
        if self._intervention_event.active:
            callback(self, *args, **kwargs)
        else:
            self._return_to_duty()
    return decorated


class Policeman(BaseActor, GeolocatedActor):
    """
    Actor which can be re-purposed by headquarters or simulation manager to dispatch it to assist other units
    Can dispatch messages to simulation manager for requesting of assistance in intervention
    Is geolocated and capable of moving around the map for fulfilling its current purpose
    """

    class PolicemanNotification(NotificationType):
        BACKUP_NEEDED = 'backup_needed'
        IN_COMBAT = 'in_combat'

    class PolicemanPurpose(ActiveActorPurpose):
        """
        Class for keeping policeman purposes
        """
        PATROL = 'patrol'
        INTERVENTION = 'intervention'
        COMBAT = 'combat'

    def __init__(self, purpose: PolicemanPurpose, location: Location, success_rate):
        super().__init__(purpose)
        super(BaseActor, self).__init__(location)
        self._last_purpose = purpose
        self.success_rate = success_rate

        self._current_route = None
        self._patrol_route = None
        self._intervention_event = None

    def re_purpose(self, purpose):
        self._store_purpose(purpose)
        super().re_purpose(purpose)

    # POLICEMAN'S API

    def dispatch_for_assistance(self, location):
        """
        Warning: This method overrides a routing action !
        This means, if a unit is dispatched during autonomous routing action,
        its destination will be overriden
        :param location: New routing location
        """
        self._route_to(CityMap.route(self.location, location))

    def dispatch_for_patrol(self, route):
        if self.purpose not in [
            Policeman.PolicemanPurpose.COMBAT,
            Policeman.PolicemanPurpose.INTERVENTION,
            Policeman.PolicemanPurpose.ROUTING,
        ]:
            self._patrol_route = route
            self.re_purpose(Policeman.PolicemanPurpose.PATROL)
        else:
            raise PolicemanError(f'Cannot send a unit to patrol while its {self.purpose}')

    def tick_action(self, notifications) -> Callable:
        def action():
            self._process_notifications(notifications)
            {
                Policeman.PolicemanPurpose.IDLE: lambda: None,
                Policeman.PolicemanPurpose.PATROL: self._patrol_actions,
                Policeman.PolicemanPurpose.ROUTING: self._routing_actions,
                Policeman.PolicemanPurpose.INTERVENTION: self._intervention_actions,
                Policeman.PolicemanPurpose.COMBAT: self._combat_actions,
            }[self.purpose]()
        return action

    # INTERNAL STATE CHANGES

    def _store_purpose(self, purpose):
        arrived_at_intervention = purpose in [
            Policeman.PolicemanPurpose.INTERVENTION,
            Policeman.PolicemanPurpose.COMBAT
        ] and self._last_purpose is Policeman.PolicemanPurpose.ROUTING
        if not arrived_at_intervention:
            self._last_purpose = self.purpose
            self._last_location = self.location

    def _route_to(self, route):
        self._current_route = route
        self.re_purpose(Policeman.PolicemanPurpose.ROUTING)

    def _process_notifications(self, notifications):
        for notification in notifications:
            actions_mapping = {
                # TODO: Add more actions which influence this actor's state
                Policeman.PolicemanNotification.BACKUP_NEEDED: lambda: self._process_need_backup(notification),
            }
            defaultdict(lambda: lambda: None, actions_mapping)[notification.type]()  # Fallback to no-op if not matched

    def _try_join_event(self):  # TODO: Insert random intervention events to locations in sim manager
        intervention_event = self.location.get_intervention_event()
        if intervention_event:
            self._intervention_event = intervention_event
            intervention_event.join(self)

            if intervention_event.armed_combat:
                self.re_purpose(Policeman.PolicemanPurpose.COMBAT)
            else:
                self.re_purpose(Policeman.PolicemanPurpose.INTERVENTION)

    def _return_to_duty(self):
        if self._last_purpose is Policeman.PolicemanPurpose.PATROL:
            self.re_purpose(Policeman.PolicemanPurpose.PATROL)
        elif self._last_purpose is Policeman.PolicemanPurpose.IDLE:
            self._route_to(CityMap.route(self.location, self._last_location))

    def _send_notification_with_location(self, notification_type):
        Notifications.send(
            payload={'location': self.location},
            notification_type=notification_type,
        )

    def _process_need_backup(self, notification):
        call_location = notification.payload['location']
        # TODO: Here we can determine whether to follow the call and go to location. Some config options possibly
        self._route_to(call_location)

    # ACTIONS

    def _patrol_actions(self):
        if not self._current_route:
            self._current_route = self._patrol_route.copy()

        self.move_forward(self._current_route)
        self._try_join_event()

    @return_to_duty_if_inactive
    def _intervention_actions(self):
        if self._intervention_event.armed_combat:
            self.re_purpose(Policeman.PolicemanPurpose.COMBAT)
        else:
            self._intervention_event.mitigate(self)

    @return_to_duty_if_inactive
    def _combat_actions(self):
        if not self._intervention_event.sufficient_backup:
            notification_type = Policeman.PolicemanNotification.BACKUP_NEEDED
        else:
            notification_type = Policeman.PolicemanNotification.IN_COMBAT

        self._send_notification_with_location(notification_type=notification_type)
        self._intervention_event.mitigate(self)

    def _routing_actions(self):
        if self._current_route:
            self.move_forward(self._current_route)
            self._try_join_event()
        else:
            self.re_purpose(Policeman.PolicemanPurpose.IDLE)
