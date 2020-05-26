from smart_intervention.models.actors.management_center import ManagementCenter
from smart_intervention.models.actors.policeman.policeman import Policeman, PolicemanError


# TODO: Resolve problems with private variables access, it's fine for now

class PolicemanNotificationProcessor:

    def __init__(self, policeman):
        self._policeman = policeman

    def process(self, notifications):
        actions = [self._get_action(notification) for notification in notifications]
        for action in actions:
            action()

    def _get_action(self, notification):
        if notification.type is ManagementCenter.ManagementCenterNotification.DISPATCH_TO_GUNFIGHT:
            return lambda: self._dispatch_to_gunfight(notification.payload['location'])

        if notification.type is ManagementCenter.ManagementCenterNotification.DISPATCH_TO_INTERVENTION:
            return lambda: self._dispatch_to_intervention(notification.payload['location'])

        if notification.type is ManagementCenter.ManagementCenterNotification.DISPATCH_TO_PATROL:
            return lambda: self._dispatch_to_intervention(notification.payload['route'])

        if notification.type is ManagementCenter.ManagementCenterNotification.DISMISS_FROM_INTERVENTION_CALL:
            return lambda: self._dismiss_from_call()

        if notification.type is ManagementCenter.ManagementCenterNotification.DISMISS_FROM_GUNFIGHT_CALL:
            return lambda: self._dismiss_from_call()

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

    def _dismiss_from_call(self):
        self._policeman._return_to_duty()
