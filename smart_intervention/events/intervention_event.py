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
        self.location = location
        self._initial_health = event_health
        self._actors_by_type = defaultdict(list)

        self.event_health = event_health
        self.armed_combat = False

    def mitigate(self, actor):
        if random_decision(SimulationVariables[SimulationVariableType.GUNFIGHT_BREAKOUT_RATE]):
            # TODO: Log it
            self.armed_combat = True
            # We re-set event's health to initial health increased with contextual danger
            self.event_health = self._initial_health + (self._initial_health * self.danger_contexted)
        else:
            if actor.__class__ is Policeman:
                self.event_health -= actor.efficiency  # Simple 1-1
            elif actor.__class__ is Ambulance:
                seq = self._actors_by_type[Ambulance].index(actor)
                self.event_health -= actor.efficiency * (1 / (2 ** seq))  # Subtract by the formula

    def join(self, actor):
        # TODO: Log it
        self._actors_by_type[actor.__class__].append(actor)

    def active(self):
        return self.event_health > 0

    @property
    def danger_contexted(self):  # TODO: Implement using time contextualness here
        return self._danger * (1 + self.location.danger_factor)

    # Backup is sufficient, when participating entities can finish the intervention in one turn
    @property
    def backup_sufficient(self):
        return self.missing_efficiency <= 0

    @staticmethod
    def sum_efficiency(actors):
        return reduce(lambda acc, actor: acc + actor.efficiency, actors, 0)

    @staticmethod
    def sum_ambulances_efficiency(ambulances):
        # Each ambulance is half of the value of previous one, sorted by arrival
        return reduce(
            lambda val, tpl: val + tpl[1] * (1 / (2 ** tpl[0])),
            enumerate(ambulances, 1), 0
        )

    @staticmethod
    def sum_ambulances_and_units_efficiency(ambulances, units):
        return InterventionEvent.sum_efficiency(units) + InterventionEvent.sum_ambulances_efficiency(ambulances)

    @property
    def missing_efficiency(self):
        return self.event_health - self.sum_ambulances_and_units_efficiency(
            self._actors_by_type[Policeman], self._actors_by_type[Ambulance]
        )
