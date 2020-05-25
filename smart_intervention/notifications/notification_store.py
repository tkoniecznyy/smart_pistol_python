from dataclasses import dataclass
from enum import Enum
from typing import List

import dataclasses as dc

from smart_intervention.models.actors.bases import BaseActor


class NotificationType(Enum):
    pass


@dataclass
class Notification:
    """
    Base class for notifications
    """
    type: NotificationType = dc.field()
    actor: BaseActor = dc.field()
    payload: dict = dc.field(default_factory=dict)


class NotificationStore:
    """
    Class which is responsible for notification distribution between entities that are allowed to receive them
    """

    def __init__(self):
        self.notifications = []
        self.cache = []

    def send(self, notification_type, actor, payload):
        self.notifications.append(Notification(notification_type, payload, actor))

    def flush(self) -> List[Notification]:
        self.cache += self.notifications  # Store this for viewing later in the report
        values = self.notifications
        self.notifications = []
        return values
