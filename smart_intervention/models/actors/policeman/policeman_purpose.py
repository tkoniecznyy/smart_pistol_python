from enum import Enum


class PolicemanPurpose(Enum):
    """
    Class for keeping policeman purposes
    """
    IDLE = 'idle'
    PATROL = 'patrol'
    INTERVENTION = 'intervention'
    GUNFIGHT = 'gunfight'
    ROUTING_TO_INTERVENTION = 'routing_to_intervention'
    ROUTING_TO_GUNFIGHT = 'routing_to_combat'
