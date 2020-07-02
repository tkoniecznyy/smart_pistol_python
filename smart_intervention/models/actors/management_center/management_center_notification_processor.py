from collections import defaultdict

from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import \
    AmbulanceHeadquarterNotification
from smart_intervention.models.actors.policeman.policeman_notification import PolicemanNotification
from smart_intervention.utils.processing import mass_process


class ManagementCenterNotificationProcessor:
    def __init__(self, management_center):
        self._management_center = management_center

    def process(self, notifications):
        notifications_by_type = self._filter_processable(notifications.by_type())

        # Policeman notifications processing
        self._process_returning_to_duty_notifications(notifications_by_type[PolicemanNotification.RETURNING_TO_DUTY])
        self._process_intervention_notifications(notifications_by_type[PolicemanNotification.INTERVENTION])
        self._process_gunfight_notifications(notifications_by_type[PolicemanNotification.GUNFIGHT])
        self._process_backup_needed_notifications(notifications_by_type[PolicemanNotification.BACKUP_NEEDED])

        # Ambulance HQ notifications processing
        self._process_ambulance_request_accepted_notifications(
            notifications_by_type[AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_ACCEPTED]
        )
        self._process_ambulance_request_rejected_notifications(
            notifications_by_type[AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_REJECTED]
        )

    @staticmethod
    def _filter_processable(notifications_by_type):
        processable_types = [
            PolicemanNotification.BACKUP_NEEDED,
            PolicemanNotification.GUNFIGHT,
            PolicemanNotification.INTERVENTION,
            PolicemanNotification.RETURNING_TO_DUTY,
            AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_REJECTED,
            AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_ACCEPTED,
        ]

        return defaultdict(list, {
            notification_type: values
            for notification_type, values in notifications_by_type.items()
            if notification_type in processable_types
        })

    def _process_backup_needed_notifications(self, notifications):
        # TODO: Store messages in analytic model and observe redundancy in signal sending
        for event in self._cluster_backup_needed_by_event(notifications).keys():
            self._management_center.process_backup_needed(event)

    @staticmethod
    def _cluster_backup_needed_by_event(notifications):
        clustered_notifications = defaultdict(list)

        def process_one(notification):
            location = notification.payload['location']
            event = location.intervention_event
            if event.active:
                clustered_notifications[event].append(notification)
            else:
                # This is a no-op
                raise RuntimeWarning('A backup needed notification has been received from a finished event')

        for notification in notifications:
            process_one(notification)

        return clustered_notifications

    @mass_process
    def _process_gunfight_notifications(self, notifications):
        def process_one(notification):
            location = notification.payload['location']
            self._management_center.acknowledge_gunfight(
                location.intervention_event,
                notification.actor
            )

        return notifications, process_one

    @mass_process
    def _process_intervention_notifications(self, notifications):
        def process_one(notification):
            location = notification.payload['location']
            self._management_center.acknowledge_intervention(
                location.intervention_event,
                notification.actor
            )

        return notifications, process_one

    @mass_process
    def _process_returning_to_duty_notifications(self, notifications):
        def process_one(notification):
            self._management_center.acknowledge_return_to_duty(notification.actor)

        return notifications, process_one

    @mass_process
    def _process_ambulance_request_rejected_notifications(self, notifications):
        def process_one(notification):
            location = notification.payload['location']
            self._management_center.acknowledge_reject_ambulance_request(
                location.intervention_event
            )

        return notifications, process_one

    @mass_process
    def _process_ambulance_request_accepted_notifications(self, notifications):
        def process_one(notification):
            location = notification.payload['location']
            ambulance = notification.payload['ambulance']
            self._management_center.acknowledge_accept_ambulance_request(
                location.intervention_event,
                ambulance
            )

        return notifications, process_one
