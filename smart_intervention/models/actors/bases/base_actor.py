from abc import ABC, abstractmethod
from typing import Callable

from smart_intervention.models.actors.bases.purpose import Purpose


class BaseActor(ABC):

    def __init__(self, purpose: Purpose):
        self.purpose = purpose

    @abstractmethod
    def re_purpose(self, purpose: Purpose):
        """
        Primary purpose change of the actor
        """
        self.purpose = purpose

    @abstractmethod
    def tick_action(self, notifications) -> Callable:
        """
        Function for an actor, which retrieves its' state updating logic
        :return: A callable which is responsible for actor internal state changes in next simulation tick step
        """
        pass
