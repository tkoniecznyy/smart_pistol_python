from smart_intervention import Notifications
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import \
    AmbulanceHeadquarterNotification
from smart_intervention.models.actors.management_center.management_center_notification import \
    ManagementCenterNotification
from smart_intervention.utils.processing import mass_process


class AmbulanceHeadquarterNotificationProcessor:
    def __init__(self, management_center):
        self._management_center = management_center

    def process(self, notifications):
        notifications_by_type = self._filter_processable(notifications.by_type())

        self._process_assistance_requests(
            notifications_by_type[ManagementCenterNotification.REQUEST_AMBULANCE_ASSISTANCE]
        )

    @staticmethod
    def _filter_processable(notifications_by_type):  # TODO: Refactor - generalize (extract to parent class)
        # TODO: Add processing of return to duty from ambulance when implemented
        processable_types = [
            ManagementCenterNotification.REQUEST_AMBULANCE_ASSISTANCE
        ]
        return {
            notification_type: values
            for notification_type, values in notifications_by_type.items()
            if notification_type in processable_types
        }

    @mass_process
    def _process_assistance_requests(self, notifications):
        def process_one(notification):
            event = notification.event

            ambulance = self._management_center.dispatch_ambulance_to(event)
            if ambulance:
                Notifications.send(
                    AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_ACCEPTED,
                    self,
                    payload={
                        'location': event.location,
                        'ambulance': ambulance,
                    }
                )
            else:
                Notifications.send(
                    AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_REJECTED,
                    self,
                    payload={
                        'location': event.location,
                    }
                )

        return notifications, process_one
