from typing import Callable

from smart_intervention import CityMap, Notifications
from smart_intervention.models.actors.bases import BaseActor
from smart_intervention.models.actors.management_center.management_center_notification import \
    ManagementCenterNotification
from smart_intervention.models.actors.management_center.management_center_notification_processor import \
    ManagementCenterNotificationProcessor
from smart_intervention.models.actors.management_center.resource_monitor import (
    ManagementCenterResourceMonitor,
    ResourceState,
)


class ManagementCenter(BaseActor):

    def __init__(self, managed_units):
        self._resource_monitor = ManagementCenterResourceMonitor()
        for unit in managed_units:
            self._resource_monitor.set_unit_state(unit, ResourceState.AVAILABLE)

    def tick_action(self, notifications) -> Callable:
        processable_notifications = notifications.get_notifications_for_processing(self)

        def action():
            ManagementCenterNotificationProcessor(self).process(processable_notifications)
            self._process_interventions()

        return action

    def acknowledge_intervention(self, event, actor):
        self._resource_monitor.set_unit_state(actor, ResourceState.INTERVENTION, event)

    def acknowledge_in_combat(self, event, actor):
        self._resource_monitor.set_unit_state(actor, ResourceState.GUNFIGHT, event)

    def acknowledge_return_to_duty(self, actor):
        self._resource_monitor.set_unit_state(actor, ResourceState.AVAILABLE)

    def acknowledge_reject_ambulance_request(self, event):
        self._resource_monitor.set_ambulances_unavailable(event)

    def acknowledge_accept_ambulance_request(self, event, actor):
        self._resource_monitor.set_ambulance_state(actor, ResourceState.DISPATCHED, event)

    def process_backup_needed(self, event):
        if event.active:
            if not event.backup_sufficient:
                self._send_policemen_backup(event)

    def _send_policemen_backup(self, event):
        missing_efficiency = event.missing_efficiency
        policemen = []
        available_policemen = self._resource_monitor.get_available_units()
        missing_efficiency = self._take_close_policemen(
            missing_efficiency, event.location, available_policemen, policemen
        )

        if missing_efficiency > 0:
            dispatched_policemen = self._resource_monitor.get_dispatched_to_intervention_units()
            missing_efficiency = self._take_close_policemen(
                missing_efficiency, event.location, dispatched_policemen, policemen
            )

            if missing_efficiency > 0:
                intervening_policemen = self._resource_monitor.get_intervening_units()
                self._take_close_policemen(
                    missing_efficiency, event.location, intervening_policemen, policemen
                )
        for policeman in policemen:
            Notifications.send(
                ManagementCenterNotification.DISPATCH_TO_GUNFIGHT, self,
                payload={
                    'location': event.location,
                    'policeman': policeman
                }
            )

    def _take_close_policemen(self, missing_efficiency, location, policemen_pool, policemen_to_take):
        policemen = self._sort_closest(policemen_pool, location)
        while missing_efficiency > 0 and policemen:
            next_policeman = policemen.pop(0)
            policemen_to_take.append(next_policeman)
            missing_efficiency -= next_policeman.efficiency
        return missing_efficiency

    @staticmethod
    def _sort_closest(units, location, k=1):
        policemen_distances = [
            (CityMap.get_distance(policeman.location, location), policeman)
            for policeman in units
        ]
        policemen_distances.sort(key=lambda x: x[0])
        sorted_policemen = [tpl[1] for tpl in policemen_distances]
        return sorted_policemen[:k]

    def _process_interventions(self):
        raise NotImplementedError  # TODO: Implement
