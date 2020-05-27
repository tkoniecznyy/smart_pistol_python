from smart_intervention.notifications.notification import NotificationType


class ManagementCenterNotification(NotificationType):
    DISPATCH_TO_INTERVENTION = 'dispatch_to_intervention'
    DISPATCH_TO_GUNFIGHT = 'dispatch_to_gunfight'
    DISPATCH_TO_PATROL = 'dispatch_to_patrol'
    DISMISS_FROM_INTERVENTION_CALL = 'dismiss_from_intervention_call'
    DISMISS_FROM_GUNFIGHT_CALL = 'dismiss_from_gunfight_call'
    REQUEST_AMBULANCE_ASSISTANCE = 'request_ambulance_assistance'
