from functools import reduce


class InterventionEvent:
    def __init__(self, danger, event_health, location):
        """
        :param danger: Double from 0 to 1, indicating chance of combat in this event
        :param event_health:  Positive integer, indicating how much time will this intervention consume
        """
        self._danger = danger
        self._location = location
        self._event_health = event_health

        self._participating_entities = []
        self._armed_combat = False

    def mitigate(self, entity):
        self._event_health -= entity.success_rate  # Simple 1-1

    def join(self, entity):
        self._participating_entities.append(entity)

    def active(self):
        return self._event_health > 0

    @property
    def armed_combat(self):
        """
        The method is calculating mean success rate, and if it's lesser than event danger, combat is not triggered
        """
        if not self._armed_combat:
            combat_triggered = self._danger_contexted > self._mean_success_rate
            self._armed_combat = combat_triggered
            return combat_triggered
        else:
            return True

    @property
    def _mean_success_rate(self):
        entities_count = len(self._participating_entities)
        return reduce(
            lambda acc, entity: acc + entity.success_rate,
            self._participating_entities
        ) / entities_count

    @property
    def _danger_contexted(self):   # TODO: Implement using time contextualness here
        return self._danger * (1 + self._location.danger_factor())
