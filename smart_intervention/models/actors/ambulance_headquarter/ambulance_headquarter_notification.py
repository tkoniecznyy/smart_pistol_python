from enum import Enum


class AmbulanceHeadquarterNotification(Enum):
    AMBULANCE_REQUEST_REJECTED = 'ambulance_request_rejected'
    AMBULANCE_REQUEST_ACCEPTED = 'ambulance_request_accepted'
    DISPATCH_TO_EVENT = 'dispatch_to_event'
