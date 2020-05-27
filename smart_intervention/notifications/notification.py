import dataclasses as dc
from dataclasses import dataclass
from enum import Enum

from smart_intervention.models.actors.ambulance.ambulance import Ambulance
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter import AmbulanceHeadquarter
from smart_intervention.models.actors.bases import BaseActor
from smart_intervention.models.actors.management_center.management_center import ManagementCenter
from smart_intervention.models.actors.policeman.policeman import Policeman
from smart_intervention.models.actors.management_center.management_center_notification import ManagementCenterNotification
from smart_intervention.models.actors.policeman.policeman_notification import PolicemanNotification
from smart_intervention.models.actors.ambulance.ambulance_notification import AmbulanceNotification
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import AmbulanceHeadquarterNotification

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

    def processed_by(self, requester):
        relevant_types_for_requester = {
            ManagementCenter: [PolicemanNotification, AmbulanceHeadquarterNotification],
            Policeman: [ManagementCenterNotification],
            AmbulanceHeadquarter: [AmbulanceNotification],
            Ambulance: [AmbulanceHeadquarterNotification],
        }[requester.__class__]
        return self.type in relevant_types_for_requester


class Notifications:

    def __init__(self):
        self._notification_list = []
        self._cache = []

    def add(self, notification):
        self._notification_list.append(notification)

    def get_all_cached(self):
        return self._cache

    def flush(self):
        self._cache += self._notification_list  # Store this for viewing later in the report
        return self

    def clear(self):
        self._notification_list = []

    def get_notifications_for_processing(self, requester):
        return [notification for notification in self._notification_list if notification.processed_by(requester)]
