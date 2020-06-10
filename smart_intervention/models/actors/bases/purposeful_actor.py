from abc import ABC

from smart_intervention.models.actors.bases import BaseActor


class PurposefulActor(BaseActor, ABC):
    def __init__(self, purpose):
        self.purpose = purpose

    def re_purpose(self, purpose):
        """
        Primary purpose change of the actor
        """
        self.purpose = purpose