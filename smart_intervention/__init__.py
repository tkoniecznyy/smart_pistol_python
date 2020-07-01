__version__ = '0.1.0'

import logging

from smart_intervention.models.actors.policeman.policeman_purpose import PolicemanPurpose
from smart_intervention.models.simulation_manager import SimulationManager
from smart_intervention.utils.iter_utils import pick_random, generate_n
from random import random

POLICEMEN_COUNT = 10
AMBULANCES_COUNT = 3
COMMAND_INSTRUCTION = 'Loop stopped, please enter command: \n\ts => step\n\texit => terminate program\n\tev => insert' \
                      ' intervention event\n'

logging.basicConfig(format='%(name)s:%(levelname)s\t%(message)s', level=logging.DEBUG)


def generate_environment_and_actors():
    from smart_intervention.models.actors.policeman.policeman import Policeman
    from smart_intervention.models.actors.ambulance.ambulance import Ambulance
    from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter import AmbulanceHeadquarter
    from smart_intervention.models.actors.management_center.management_center import ManagementCenter
    from smart_intervention.globals import CityMap

    locations = CityMap.get_locations()
    police_outposts = [pick_random(locations), pick_random(locations)]
    ambulance_hq = pick_random(locations)
    policemen = generate_n(
        lambda _: Policeman(
            purpose=PolicemanPurpose.IDLE,
            location=pick_random(police_outposts),
            efficiency=round(random(), 2)
        ),
        n=POLICEMEN_COUNT
    )
    ambulances = generate_n(
        lambda _: Ambulance(
            purpose=Ambulance.AmbulancePurpose.IDLE,
            location=ambulance_hq,
            efficiency=round(random(), 2),
            ambulance_hq=ambulance_hq
        ),
        n=AMBULANCES_COUNT
    )
    MC = ManagementCenter(policemen)
    AHQ = AmbulanceHeadquarter(ambulances)
    return [
        *policemen,
        *ambulances,
        MC,
        AHQ,
    ], police_outposts, ambulance_hq


def create_intervention():
    from smart_intervention.globals import CityMap
    from smart_intervention.events.intervention_event import InterventionEvent
    locations = CityMap.get_locations()
    location_ids = [str(id(location)) for location in locations]
    location_id = input(f'Pick a location from this list:\n{location_ids}')
    if location_id not in location_ids:
        print('ERROR: Invalid location chosen')
    else:
        location = locations[location_ids.index(location_id)]
        danger = input(
            'Pick danger index (floating point 0-1), which indicates how likely the event is to break out into gunfight')
        try:
            danger = float(danger)
        except ValueError:
            print(f'Invalid value chosen as danger level!: {danger}')

        health_index = input(
            'Pick events health index (number), which indicates how difficult it is for policemen to finish')
        try:
            health_index = float(health_index)
        except ValueError:
            print(f'Invalid value chosen as health_index level!: {health_index}')

        location.intervention_event = InterventionEvent(danger, health_index, location)


def interpret_command(input, sim_manager):
    if input == 'ev':
        create_intervention()
    if input == 's':
        sim_manager.do_tick()


def do_simple_simulation():
    initial_actors, outposts, hq = generate_environment_and_actors()
    sim_manager = SimulationManager(initial_actors)

    inp = input(COMMAND_INSTRUCTION)
    interpret_command(inp, sim_manager)
    while inp != 'exit':
        inp = input(COMMAND_INSTRUCTION)
        interpret_command(inp, sim_manager)

    print('Terminating...')


if __name__ == '__main__':
    do_simple_simulation()
