from collections import defaultdict
from functools import reduce
from smart_intervention import SimulationVariables, SimulationVariableType, Policeman
from smart_intervention.models.actors.ambulance.ambulance import Ambulance
from smart_intervention.utils.random import random_decision


class InterventionEvent:
    def __init__(self, danger, event_health, location):
        """
        :param danger: Double from 0 to 1, indicating chance of combat in this event
        :param event_health:  Positive integer, indicating how much time will this intervention consume
        """
        self._danger = danger
        self._location = location
        self._initial_health = event_health
        self._actors_by_type = defaultdict(list)

        self.event_health = event_health
        self.armed_combat = False

    def mitigate(self, actor):
        if random_decision(SimulationVariables[SimulationVariableType.GUNFIGHT_BREAKOUT_RATE]):
            self.armed_combat = True
            # We re-set event's health to initial health increased with contextual danger
            self.event_health = self._initial_health + (self._initial_health * self.danger_contexted)
        else:
            self.event_health -= actor.efficiency  # Simple 1-1

    def join(self, actor):
        self._actors_by_type[actor.__class__].append(actor)

    def active(self):
        return self.event_health > 0

    @property
    def danger_contexted(self):  # TODO: Implement using time contextualness here
        return self._danger * (1 + self._location.danger_factor)

    # FIXME: Backup is sufficient, when participating entities can finish the intervention in one turn
    @property
    def sufficient_backup(self):
        unit_manpower = self._sum_efficiency(self._actors_by_type[Policeman])


    @staticmethod
    def _sum_efficiency(actors):
        return reduce(lambda acc, actor: acc + actor.efficiency, actors, 0)

