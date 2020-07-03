from typing import List
from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention.globals import Notifications


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

    def do_tick(self):
        """
        Performs a tick of the simulation
        :return TODO Preferably some kind of a snapshot for our simulation or a step-artifact for UI (like screen shot):
        """

        last_rounds_notifications = Notifications.get_last()
        actions = [actor.tick_action(last_rounds_notifications) for actor in self.actors]
        for action in actions:
            action()

        Notifications.clear()

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

    def get_policemen(self):
        return [actor for actor in self.actors if actor.__class__.__name__ == 'Policeman']
