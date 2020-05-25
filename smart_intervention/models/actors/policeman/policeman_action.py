from smart_intervention.models.actors.action import Action
from smart_intervention.models.actors.policeman.policeman import Policeman


# TODO: Resolve problems with private variables access, it's fine for now

def return_to_duty_if_inactive(callback):
    def decorated(self, *args, **kwargs):
        if self._policeman._intervention_event.active:
            callback(self, *args, **kwargs)
        else:
            self._return_to_duty()

    return decorated


class PolicemanAction(Action):
    def __init__(self, policeman: Policeman):
        self._policeman = policeman

        self._after_init()

    def _after_init(self):
        self._action = self._get_action(self._policeman.purpose)

    def execute(self):
        self._action()

    def _get_action(self, purpose):
        return {
            Policeman.PolicemanPurpose.IDLE: lambda: None,
            Policeman.PolicemanPurpose.PATROL: self._patrol_actions,
            Policeman.PolicemanPurpose.INTERVENTION: self._intervention_actions,
            Policeman.PolicemanPurpose.GUNFIGHT: self._gunfight_actions,
            Policeman.PolicemanPurpose.ROUTING_TO_INTERVENTION: self._routing_actions,
            Policeman.PolicemanPurpose.ROUTING_TO_GUNFIGHT: self._routing_actions,
        }[purpose]

    def _patrol_actions(self):
        policeman = self._policeman
        if not policeman._current_route:
            policeman._current_route = policeman._patrol_route.copy()

        policeman.move_forward(policeman._current_route)
        policeman._try_join_event()

    @return_to_duty_if_inactive
    def _intervention_actions(self):
        policeman = self._policeman
        if policeman._intervention_event.armed_combat:
            policeman.re_purpose(Policeman.PolicemanPurpose.GUNFIGHT)
        else:
            policeman._intervention_event.mitigate(policeman)

    @return_to_duty_if_inactive
    def _gunfight_actions(self):
        policeman = self._policeman
        if not policeman._intervention_event.sufficient_backup:
            notification_type = Policeman.PolicemanNotification.BACKUP_NEEDED
        else:
            notification_type = Policeman.PolicemanNotification.IN_COMBAT

        policeman._send_notification_with_location(notification_type=notification_type)
        policeman._intervention_event.mitigate(policeman)

    def _routing_actions(self):
        policeman = self._policeman
        if policeman._current_route:
            policeman.move_forward(policeman._current_route)
            policeman._try_join_event()
        else:
            policeman.re_purpose(Policeman.PolicemanPurpose.IDLE)
