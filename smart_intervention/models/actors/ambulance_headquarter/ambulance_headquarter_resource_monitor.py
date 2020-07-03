from enum import Enum


class AmbulanceResourceState(Enum):
    AVAILABLE = 'available'
    BUSY = 'busy'


class AmbulanceHeadquarterResourceMonitor:
    def __init__(self, managed_ambulances):
        self._ambulances_by_state = {
            AmbulanceResourceState.AVAILABLE: managed_ambulances,
            AmbulanceResourceState.BUSY: [],
        }

    def set_ambulance_state(self, ambulance, state):
        for state, ambulances_in_state in self._ambulances_by_state.items():
            if ambulance in ambulances_in_state:
                self._ambulances_by_state[state] = [
                    ambulance_in_state
                    for ambulance_in_state in ambulances_in_state
                    if ambulance_in_state != ambulance
                ]
        self._ambulances_by_state[state].append(ambulance)

    def get_available_ambulances(self):
        return self._ambulances_by_state[AmbulanceResourceState.AVAILABLE]

    def add_new_ambulance(self, ambulance):
        self._ambulances_by_state[AmbulanceResourceState.AVAILABLE].append(ambulance)
