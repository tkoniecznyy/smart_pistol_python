import uuid


class Location:
    """
    Class which represents a node in the graph (location on the "city map")
    """

    def __init__(self, danger_factor=0):
        self.danger_factor = danger_factor
        self.intervention_event = None
        self.actors = []
        self.id = uuid.uuid1()

    def __hash__(self):
        return hash(self.id)

    def set_intervention_event(self, event):
        self.intervention_event = event

    def add_actors(self, actors):
        self.actors = self.actors + actors

    def add_actor(self, actor):
        self.actors = self.actors.append(actor)

    def remove_actor(self, actor):
        self.actors.remove(actor)
