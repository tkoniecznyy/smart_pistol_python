from smart_intervention.models.actors.action import Action

from smart_intervention.models.actors.policeman.policeman_notification import PolicemanNotification
from smart_intervention.models.actors.policeman.policeman_purpose import PolicemanPurpose


def return_to_duty_if_inactive(callback):
    def decorated(self, *args, **kwargs):
        event_in_location = self._policeman.location.intervention_event
        if event_in_location and event_in_location.active:
            callback(self, *args, **kwargs)
        else:
            self._policeman.return_to_duty()

    return decorated


class PolicemanAction(Action):
    def __init__(self, policeman):
        self._policeman = policeman

        self._after_init()

    def _after_init(self):
        self._action = self._get_action(self._policeman.purpose)

    def execute(self):
        self._action()

    def _get_action(self, purpose):
        return {
            PolicemanPurpose.IDLE: lambda: None,
            PolicemanPurpose.PATROL: self._patrol_actions,
            PolicemanPurpose.INTERVENTION: self._intervention_actions,
            PolicemanPurpose.GUNFIGHT: self._gunfight_actions,
            PolicemanPurpose.ROUTING_TO_INTERVENTION: self._routing_actions,
            PolicemanPurpose.ROUTING_TO_GUNFIGHT: self._routing_actions,
            PolicemanPurpose.RETURNING_TO_HQ: self._routing_actions
        }[purpose]

    def _patrol_actions(self):
        policeman = self._policeman
        if not policeman.current_route:
            policeman.current_route = policeman.patrol_route.copy()

        policeman.move_forward(policeman.current_route)
        policeman.log.info(f'Moved forward on patrol route to {policeman.location}')

    @return_to_duty_if_inactive
    def _intervention_actions(self):
        policeman = self._policeman
        if policeman.intervention_event.armed_combat:
            policeman.re_purpose(PolicemanPurpose.GUNFIGHT)
        else:
            policeman.intervention_event.mitigate(policeman)
            policeman.log.info(f'Mitigating intervention {id(policeman.intervention_event)}')
            policeman.send_notification(notification_type=PolicemanNotification.INTERVENTION)

    @return_to_duty_if_inactive
    def _gunfight_actions(self):
        policeman = self._policeman
        if not policeman.intervention_event.backup_sufficient:
            notification_type = PolicemanNotification.BACKUP_NEEDED
        else:
            notification_type = PolicemanNotification.GUNFIGHT

        policeman.intervention_event.mitigate(policeman)
        policeman.log.info(f'Mitigating gunfight {id(policeman.intervention_event)}')
        policeman.send_notification_with_location(notification_type=notification_type)

    def _routing_actions(self):
        policeman = self._policeman
        try:
            policeman.move_and_join_event()
        except Exception:
            policeman.re_purpose(PolicemanPurpose.IDLE)
