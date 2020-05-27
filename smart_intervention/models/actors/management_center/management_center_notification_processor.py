from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter_notification import \
    AmbulanceHeadquarterNotification
from smart_intervention.models.actors.management_center.management_center_notification import \
    ManagementCenterNotification
from smart_intervention.models.actors.policeman.policeman_notification import PolicemanNotification


class ManagementCenterNotificationProcessor:
    def __init__(self, management_center):
        self._management_center = management_center

    def process(self, notifications):
        notifications_by_type = self._notifications_by_type(notifications)

        self._process_backup_needed_notifications(notifications_by_type[PolicemanNotification.BACKUP_NEEDED])
        self._process_in_combat_notifications(notifications_by_type[PolicemanNotification.GUNFIGHT])
        self._process_intervention_notifications(notifications_by_type[PolicemanNotification.INTERVENTION])

    @staticmethod
    def _notifications_by_type(notifications):
        notifications_by_type = {
            PolicemanNotification.BACKUP_NEEDED: [],
            PolicemanNotification.GUNFIGHT: [],
            PolicemanNotification.INTERVENTION: [],
            PolicemanNotification.RETURNING_TO_DUTY: [],
            AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_REJECTED: [],
            AmbulanceHeadquarterNotification.AMBULANCE_REQUEST_ACCEPTED: [],
        }
        for notification in notifications:
            notifications_by_type[notification.type].append(notification)
        return notifications_by_type

    def _process_backup_needed_notifications(self, notifications):
        def process_one(notification):
            location = notification.payload['location']
            event = location.get_intervention_event()

            if event.active:
                if event.armed_combat:
                    self._management_center.find_and_dispatch_available_units(
                        event,
                        notification_type=ManagementCenterNotification.DISPATCH_TO_GUNFIGHT
                    )
                else:
                    self._management_center.find_and_dispatch_available_units(
                        event,
                        notification_type=ManagementCenterNotification.DISPATCH_TO_INTERVENTION
                    )
            else:
                # This is a no-op
                raise RuntimeWarning('A backup needed notification has been received from a finished event')

        for notification in notifications:
            process_one(notification)

    def _process_in_combat_notifications(self, param):
        def process_one(notification):
            pass

        raise NotImplementedError  # TODO: Implement

    def _process_intervention_notifications(self, param):
        def process_one(notification):
            pass

        raise NotImplementedError  # TODO: Implement
