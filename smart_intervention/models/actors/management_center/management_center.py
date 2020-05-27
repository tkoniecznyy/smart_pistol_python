from typing import Callable

from smart_intervention.models.actors.bases import BaseActor
from smart_intervention import CityMap
from smart_intervention.models.actors.management_center.management_center_notification_processor import \
    ManagementCenterNotificationProcessor


class ManagementCenter(BaseActor):

    def __init__(self, managed_actors):
        self._managed_actors = managed_actors

    def tick_action(self, notifications) -> Callable:
        processable_notifications = notifications.get_notifications_for_processing(self)

        def action():
            ManagementCenterNotificationProcessor(self).process(processable_notifications)
        return action

    def request_ambulance(self, location):
        pass  # TODO: Implement

    def dispatch_unit(self, location):
        pass  # TODO: Implement

    def find_nearest_unit(self, location):
        pass   # TODO: Implement

    def find_and_dispatch_nearest_units(self, event, dispatch_type):
        pass  # TODO: Implement, this method needs to check if units have already been dispatched

    def acesss_danger(self, event):
        """
        :param event: Event which needs to be acessed
        :return: Dict with entries which indicate needed support in event
        {
            'ambulances': <numerical>,
            'units': <numerical>,
        }
        """
        pass  # TODO: Implement

    def dismiss_all_dispatched_units(self, location):
        pass

