from typing import Callable

from smart_intervention.globals import Notifications, CityMap
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import \
    AmbulanceHeadquarterNotification
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification_processor import \
    AmbulanceHeadquarterNotificationProcessor
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_resource_monitor import \
    (
    AmbulanceHeadquarterResourceMonitor, AmbulanceResourceState,
)
from smart_intervention.models.actors.bases import BaseActor


class AmbulanceHeadquarter(BaseActor):
    def __init__(self, managed_ambulances):
        self._resource_monitor = AmbulanceHeadquarterResourceMonitor(managed_ambulances)

    def tick_action(self, notifications) -> Callable:
        processable_notifications = notifications.get_notifications_for_processing(self)

        def action():
            AmbulanceHeadquarterNotificationProcessor(self).process(processable_notifications)

        return action

    def acknowledge_return_to_duty(self, ambulance):
        self._resource_monitor.set_ambulance_state(ambulance, AmbulanceResourceState.AVAILABLE)

    @staticmethod
    def _by_proximity(ambulances, location):  # TODO: Refactor - generalize ( move to map )
        ambulance_distances = [
            (CityMap.get_distance(ambulance.location, location), ambulance)
            for ambulance in ambulances
        ]
        ambulance_distances.sort(key=lambda x: x[0])
        return [tpl[1] for tpl in ambulance_distances]

    def dispatch_ambulance_to(self, event):
        available_ambulances = self._resource_monitor.get_available_ambulances()
        if available_ambulances:
            ambulances_by_proximity = self._by_proximity(available_ambulances, event.location)
            ambulance = ambulances_by_proximity[0]
            self._resource_monitor.set_ambulance_state(ambulance, AmbulanceResourceState.BUSY)
            Notifications.send(
                AmbulanceHeadquarterNotification.DISPATCH_TO_EVENT, self,
                payload={
                    'location': event.location,
                    'ambulance': ambulance,
                }
            )
            return ambulance
        else:
            return False
