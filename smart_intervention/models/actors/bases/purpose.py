from enum import Enum


class Purpose(Enum):
    """
    Base class for defining possible actor's purposes
    """
    pass


class PassiveActorPurpose(Purpose):
    IDLE = 'idle'


class AssistingActorPurpose(PassiveActorPurpose):
    ROUTING_TO_ASSIST = 'routing_to_assist'
