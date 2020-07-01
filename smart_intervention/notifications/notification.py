import dataclasses as dc
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
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

    def processed_by(self, requester):
        # FIXME: See if this nested import is solvable other way
        from smart_intervention.models.actors.ambulance.ambulance import Ambulance
        from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter import AmbulanceHeadquarter

        from smart_intervention.models.actors.management_center.management_center import ManagementCenter
        from smart_intervention.models.actors.policeman.policeman import Policeman
        from smart_intervention.models.actors.management_center.management_center_notification import \
            ManagementCenterNotification
        from smart_intervention.models.actors.policeman.policeman_notification import PolicemanNotification
        from smart_intervention.models.actors.ambulance.ambulance_notification import AmbulanceNotification
        from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import \
            AmbulanceHeadquarterNotification

        relevant_types_for_requester = defaultdict(list, {
            ManagementCenter: [PolicemanNotification],
            AmbulanceHeadquarter: [AmbulanceNotification],
            Ambulance: [AmbulanceHeadquarterNotification],
        })[requester.__class__]

        relevant_instances_for_requester = defaultdict(list,{
            ManagementCenter: [
                AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_ACCEPTED,
                AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_REJECTED,
                AmbulanceNotification.ASSISTING,
            ],
            Policeman: [
                ManagementCenterNotification.DISPATCH_TO_GUNFIGHT,
                ManagementCenterNotification.DISPATCH_TO_INTERVENTION,
                ManagementCenterNotification.DISPATCH_TO_PATROL,
                ManagementCenterNotification.DISMISS_FROM_GUNFIGHT_CALL,
                ManagementCenterNotification.DISMISS_FROM_INTERVENTION_CALL,
            ],
        })[requester.__class__]
        return self.type.__class__ in relevant_types_for_requester or self.type in relevant_instances_for_requester


class NotificationStore:

    def __init__(self, notification_list=None):
        self._notification_list = notification_list or []
        self._last = []

    def add(self, notification):
        self._notification_list.append(notification)

    def clear(self):
        self._last = self._notification_list
        self._notification_list = []

    def get_last(self):
        return NotificationStore(self._last)

    def get_notifications_for_processing(self, requester):
        return NotificationStore([
            notification for notification in self._notification_list if notification.processed_by(requester)
        ])

    def by_type(self):
        notifications_by_type = defaultdict(list)
        for notification in self._notification_list:
            notifications_by_type[notification.type].append(notification)
        return notifications_by_type

    def get(self):
        return self._notification_list

    def send(self, type, actor, payload):
        self.add(Notification(type, actor, payload))
