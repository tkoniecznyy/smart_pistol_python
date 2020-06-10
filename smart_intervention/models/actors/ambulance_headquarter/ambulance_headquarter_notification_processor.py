from smart_intervention import Notifications
from smart_intervention.models.actors.ambulance.ambulance_notification import AmbulanceNotification
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import \
    AmbulanceHeadquarterNotification
from smart_intervention.models.actors.management_center.management_center_notification import \
    ManagementCenterNotification
from smart_intervention.utils.processing import mass_process


class AmbulanceHeadquarterNotificationProcessor:
    def __init__(self, ambulance_hq):
        self._ambulance_hq = ambulance_hq

    def process(self, notifications):
        notifications_by_type = self._filter_processable(notifications.by_type())

        self._process_assistance_requests(
            notifications_by_type[ManagementCenterNotification.REQUEST_AMBULANCE_ASSISTANCE]
        )
        self._process_returning_ambulances(
            notifications_by_type[AmbulanceNotification.RETURNING_TO_HQ]
        )

    @staticmethod
    def _filter_processable(notifications_by_type):  # TODO: Refactor - generalize (extract to parent class)
        # TODO: Add processing of return to duty from ambulance when implemented
        processable_types = [
            ManagementCenterNotification.REQUEST_AMBULANCE_ASSISTANCE,
            AmbulanceNotification.RETURNING_TO_HQ,
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

            ambulance = self._ambulance_hq.dispatch_ambulance_to(event)
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

    @mass_process
    def _process_returning_ambulances(self, notifications):
        def process_one(notification):
            actor = notification.actor
            self._ambulance_hq.acknowledge_return_to_duty(actor)

        return notifications, process_one



