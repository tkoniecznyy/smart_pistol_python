from typing import Callable

from smart_intervention.models.actors.bases import BaseActor
from smart_intervention.models.actors.management_center.management_center_notification_processor import \
    ManagementCenterNotificationProcessor
from smart_intervention.models.actors.management_center.resource_monitor import (
    ManagementCenterResourceMonitor,
    ResourceState,
)


class ManagementCenter(BaseActor):

    def __init__(self):
        self._resource_monitor = ManagementCenterResourceMonitor()

    def tick_action(self, notifications) -> Callable:
        processable_notifications = notifications.get_notifications_for_processing(self)

        def action():
            ManagementCenterNotificationProcessor(self).process(processable_notifications)

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

