from typing import Callable

from smart_intervention.models.actors.bases import BaseActor


class Headquarter(BaseActor):
    def tick_action(self, notifications) -> Callable:
        pass

