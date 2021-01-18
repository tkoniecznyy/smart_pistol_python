from typing import List

from smart_intervention import PolicemanPurpose, AmbulancePurpose
from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.globals import notifications, CityMap
import csv

CSV_ROWS = [
    'Tura',
    'Komunikaty Wysłane',
    'Komunikaty Odebrane',
    'Interwencje Aktywne',
    'Ruchy na mapie',
    'Ilość ambulansów',
    'Ilość policjantów',
    'Ruchy Ambulansów',
    'Ruchy Policjantów',
    'Interweniujący Policjanci',
    'Patrolujący Policjanci',
    'Pomagające Ambulansy'
]


def _init_csv_logfile():
    file = open('./simulation_log.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(CSV_ROWS)
    return writer


class SimulationManager:
    """
    This class acts as a simulation supervisor, to provide control over flow of actions
    It emulates smart-system's behaviour by re-purposing actors which do not require headquarter supervision
    It also needs to give the user ability to pause actions at any given time
    """

    def __init__(self, police_outposts, ambulance_hq, actors: List[BaseActor] = None):
        if not actors:
            actors = []
        self.actors = actors
        self.police_outposts = police_outposts
        self.ambulance_hq = ambulance_hq
        self.csv_writer = _init_csv_logfile()
        self.turn = 0

    def do_tick(self):
        """
        Performs a tick of the simulation
        :return Log line
        """

        notifications.clear_received()
        last_rounds_notifications = notifications.get_last()
        notifications.clear()
        self.turn += 1
        actions = [actor.tick_action(last_rounds_notifications) for actor in self.actors]
        for action in actions:
            action()

        number_notifications = len(last_rounds_notifications.get())
        active_interventions = len(CityMap.get_interventions())
        self._csv_log([
            self.turn,
            number_notifications,
            notifications.received,
            active_interventions,
            CityMap.moves,
            len(self.get_ambulances()),
            len(self.get_policemen()),
            CityMap.ambulance_moves,
            CityMap.policeman_moves,
            len(self.intervening_policemen()),
            len(self.patroling_policemen()),
            len(self.assisting_ambulances())
        ]
        )

        CityMap.clear_moves()

    @staticmethod
    def get_actor_type(actor):
        return actor.__class__.__name__

    def get_actor_by_type(self, actor_type):
        return next(act for act in self.actors if self.get_actor_type(act) == actor_type)

    def add_actor(self, actor: BaseActor):
        self.actors.append(actor)
        actor_type = self.get_actor_type(actor)

        if actor_type == 'Policeman':
            self.get_actor_by_type('ManagementCenter').add_managed_unit(actor)

        elif actor_type == 'Ambulance':
            self.get_actor_by_type('AmbulanceManagementCenter').add_managed_ambulance(actor)

    def get_actors_by_type(self, type):
        return [actor for actor in self.actors if actor.__class__.__name__ == type]

    def get_policemen(self):
        return self.get_actors_by_type('Policeman')

    def get_ambulances(self):
        return self.get_actors_by_type('Ambulance')

    def intervening_policemen(self):
        return [
            actor for actor in self.get_actors_by_type('Policeman')
            if actor.purpose == PolicemanPurpose.INTERVENTION
        ]

    def patroling_policemen(self):
        return [
            actor for actor in self.get_actors_by_type('Policeman')
            if actor.purpose == PolicemanPurpose.PATROL
        ]

    def assisting_ambulances(self):
        return [
            actor for actor in self.get_actors_by_type('Ambulance')
            if actor.purpose == AmbulancePurpose.ASSISTING
        ]

    def _csv_log(self, array):
        self.csv_writer.writerow(array)
