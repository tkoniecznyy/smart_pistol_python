from enum import Enum


class Purpose(Enum):
    """
    Base class for defining possible actor's purposes
    """
    pass


class PassiveActorPurpose(Purpose):
    IDLE = 'idle'


class ActiveActorPurpose(PassiveActorPurpose):
    ENROUTE_ASSISTANCE = 'enroute_assistance'
    ASSISTING = 'assisting'
