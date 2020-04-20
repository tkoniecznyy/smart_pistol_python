from abc import ABC


class MessagingEntity(ABC):
    """
    An abstract base class which subclasses of are messaging
    """

    def send(self):
        pass

    def receive(self, message):
        pass
