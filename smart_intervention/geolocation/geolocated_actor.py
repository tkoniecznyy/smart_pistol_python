from abc import ABC, abstractmethod


class GeolocatedActor(ABC):
    """
    Actor which must provide its location on call
    """

    def __init__(self, location):
        self._location = location

    @abstractmethod
    def location(self):
        pass
