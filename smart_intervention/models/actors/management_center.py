from smart_intervention.notifications.notification_store import NotificationType


class ManagementCenter:
    class ManagementCenterNotification(NotificationType):
        DISPATCH_TO_INTERVENTION = 'dispatch_to_intervention'
        DISPATCH_TO_GUNFIGHT = 'dispatch_to_gunfight'
        DISPATCH_TO_PATROL = 'dispatch_to_patrol'
