from typing import Callable

from smart_intervention.models.actors.bases import BaseActor
from smart_intervention.notifications.notification_store import NotificationType


class ManagementCenter(BaseActor):

    def __init__(self, managed_actors):
        self._managed_actors = managed_actors

    def tick_action(self, notifications) -> Callable:
        def action():
            for actor in self._managed_actors:
                self._manage(actor)

        return action

    def _manage(self, actor):
        pass  # TODO: Implement

    class ManagementCenterNotification(NotificationType):
        DISPATCH_TO_INTERVENTION = 'dispatch_to_intervention'
        DISPATCH_TO_GUNFIGHT = 'dispatch_to_gunfight'
        DISPATCH_TO_PATROL = 'dispatch_to_patrol'
        DISMISS_FROM_INTERVENTION_CALL = 'dismiss_from_intervention_call'
        DISMISS_FROM_GUNFIGHT_CALL = 'dismiss_from_gunfight_call'
