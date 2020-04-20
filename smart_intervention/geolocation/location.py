from dataclasses import dataclass, field
import uuid
from typing import List

from smart_intervention.models.actors.bases.base_actor import BaseActor


@dataclass(frozen=True, eq=True)
class Location:
    """
    Class which represents a node in the graph (location on the "city map")
    """
    id: str = field(default_factory=uuid.uuid1)
    actors: List[BaseActor] = field(default_factory=list)

    def __hash__(self):
        return hash(self.id)
