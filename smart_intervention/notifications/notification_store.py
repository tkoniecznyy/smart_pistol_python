from smart_intervention.notifications.notification import Notification, Notifications


# TODO: Remove this facade

class NotificationStore:
    """
    Class which is responsible for notification distribution between entities that are allowed to receive them
    """

    def __init__(self):
        self.notifications = Notifications()

    def send(self, notification_type, actor, payload):
        self.notifications.add(Notification(notification_type, payload, actor))

    def flush(self):
        return self.notifications.flush()

    def clear(self):
        self.notifications.clear()

