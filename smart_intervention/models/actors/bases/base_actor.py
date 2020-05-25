from abc import ABC, abstractmethod
from typing import Callable


class BaseActor(ABC):
    @abstractmethod
    def tick_action(self, notifications) -> Callable:
        """
        Function for an actor, which retrieves its' state updating logic
        :return: A callable which is responsible for actor internal state changes in next simulation tick step
        """
        pass
