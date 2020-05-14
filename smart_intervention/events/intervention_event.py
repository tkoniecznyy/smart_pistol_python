from functools import reduce


class InterventionEvent:
    def __init__(self, danger, event_health):
        """
        :param danger: Double from 0 to 1, indicating chance of combat in this event
        :param event_health:  Positive integer, indicating how much time will this intervention consume
        """
        self._danger = danger
        self._participating_entities = []
        self._event_health = event_health
        self._armed_combat = False

    def mitigate(self, entity):
        # TODO: Reduce danger of event with mitigation?
        self._event_health -= entity.success_rate  # Simple 1-1

    def join(self, entity):
        # TODO: Reduce danger of event with joining entities?
        self._participating_entities.append(entity)

    def active(self):
        return self._event_health > 0

    @property
    def armed_combat(self):
        """
        The method is calculating mean success rate, and if it's lesser than event danger, combat is not triggered
        """
        if not self._armed_combat:
            entities_count = len(self._participating_entities)
            entities_success_rates_sum = reduce(lambda acc, entity: acc + entity.success_rate, self._participating_entities)
            combat_triggered = self._danger > entities_count / entities_success_rates_sum
            self._armed_combat = combat_triggered
            return combat_triggered
        else:
            return True
