from enum import Enum


class AmbulancePurpose(Enum):
    IDLE = 'idle'
    ROUTING_TO_ASSIST = 'routing_to_assist'
    ASSISTING = 'assisting'
    ROUTING_TO_HQ = 'routing_to_hq'
