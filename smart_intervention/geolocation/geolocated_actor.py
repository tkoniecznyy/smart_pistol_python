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

    def move_forward(self):
        """
        Method which moves the actor towards its target
        :return:
        """
        self._progress += 1  # This is a indicator of how far the actor has traveled on the path

    def set_target(self, target):

