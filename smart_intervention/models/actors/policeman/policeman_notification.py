from smart_intervention.notifications.notification import NotificationType


class PolicemanNotification(NotificationType):
    BACKUP_NEEDED = 'backup_needed'
    GUNFIGHT = 'gunfight'
    INTERVENTION = 'intervention'
    RETURNING_TO_DUTY = 'returning_to_duty'
