from smart_intervention.models.actors.management_center import ManagementCenter
from smart_intervention.models.actors.policeman.policeman import Policeman, PolicemanError
from collections import defaultdict


class PolicemanNotificationProcessor:

    def __init__(self, policeman):
        self._policeman = policeman

    def process(self, notifications):
        actions = defaultdict(list)
        for notification in notifications:
            action = self._get_action(notification)
            actions[notification.type].append(action)

        actions = self._choose_actions(actions)
        for action in actions:
            action()

    def _get_action(self, notification):
        if notification.type is ManagementCenter.ManagementCenterNotification.DISPATCH_TO_GUNFIGHT:
            return lambda: self._dispatch_to_gunfight(notification.payload['location'])
        if notification.type is ManagementCenter.ManagementCenterNotification.DISPATCH_TO_INTERVENTION:
            return lambda: self._dispatch_to_intervention(notification.payload['location'])
        if notification.type is ManagementCenter.ManagementCenterNotification.DISPATCH_TO_PATROL:
            return lambda: self._dispatch_to_intervention(notification.payload['route'])

    def _choose_actions(self, actions):
        notification_type_priorities = [
            ManagementCenter.ManagementCenterNotification.DISPATCH_TO_GUNFIGHT,
            ManagementCenter.ManagementCenterNotification.DISPATCH_TO_INTERVENTION,
            ManagementCenter.ManagementCenterNotification.DISPATCH_TO_PATROL,
        ]
        for notification_type in notification_type_priorities:
            act = self._first_action_by_notification_type(actions, notification_type)
            if act:
                return [act]  # TODO: Other notifications then dispatch? Only one dispatch allowed in processing

    @staticmethod
    def _first_action_by_notification_type(actions, notification_type):
        actions_list = actions[notification_type]
        try:
            return actions_list[0]
        except IndexError:
            return None

    def _dispatch_to_intervention(self, location):
        self._policeman._route_with_purpose(location, Policeman.PolicemanPurpose.ROUTING_TO_INTERVENTION)

    def _dispatch_to_gunfight(self, location):
        self._policeman._route_with_purpose(location, Policeman.PolicemanPurpose.ROUTING_TO_GUNFIGHT)

    def _dispatch_to_patrol(self, route):
        policeman = self._policeman
        if policeman.purpose not in [
            Policeman.PolicemanPurpose.GUNFIGHT,
            Policeman.PolicemanPurpose.INTERVENTION,
        ]:
            policeman._patrol_route = route
            policeman.re_purpose(Policeman.PolicemanPurpose.PATROL)
        else:
            raise PolicemanError(f'Cannot send a unit to patrol while its {policeman.purpose}')
