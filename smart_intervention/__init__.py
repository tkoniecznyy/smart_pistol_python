__version__ = '0.1.0'

import logging

from smart_intervention.models.actors.ambulance.ambulance_purpose import AmbulancePurpose
from smart_intervention.models.actors.policeman.policeman_purpose import PolicemanPurpose
from smart_intervention.models.actors.ambulance.ambulance_purpose import AmbulancePurpose
from smart_intervention.models.simulation_manager import SimulationManager
from smart_intervention.utils.iter_utils import pick_random, generate_n
from random import random

from smart_intervention.utils.random import random_decision

POLICEMEN_COUNT = 10
AMBULANCES_COUNT = 3
COMMAND_INSTRUCTION = 'Loop stopped, please enter command: \n\ts => step\n\tev => insert ' \
                      'intervention event\n\tau => add policeman/ambulance\n\tpt => send policeman for patrol\n\trc ' \
                      '=> recall policeman back to hq\n\texit => terminate program\n '

logging.basicConfig(format='%(name)s:%(levelname)s\t%(message)s', level=logging.INFO)


def generate_environment_and_actors():
    from smart_intervention.models.actors.policeman.policeman import Policeman
    from smart_intervention.models.actors.ambulance.ambulance import Ambulance
    from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter import AmbulanceHeadquarter
    from smart_intervention.models.actors.management_center.management_center import ManagementCenter
    from smart_intervention.globals import CityMap

    locations = CityMap.get_locations()
    police_outposts = [pick_random(locations), pick_random(locations)]
    ambulance_hq = pick_random(locations)

    print('Starting parameters:', flush=True)

    def gen_policeman(_):
        hq = pick_random(police_outposts)
        policeman = Policeman(
            purpose=PolicemanPurpose.IDLE,
            location=hq,
            efficiency=round(random(), 2),
            policeman_hq=hq
        )
        print(f'Policeman:\n\tEfficiency: {policeman.efficiency}\n\tPolice outpost: {id(policeman.policeman_hq)}', flush=True)
        return policeman

    policemen = generate_n(
        gen_policeman,
        n=POLICEMEN_COUNT
    )

    def gen_ambulance(_):
        amb = Ambulance(
            purpose=AmbulancePurpose.IDLE,
            location=ambulance_hq,
            efficiency=round(random(), 2),
            ambulance_hq=ambulance_hq
        )
        print(f'Ambulance:\n\tEfficiency: {amb.efficiency}\n\tHeadquarter: {id(amb.ambulance_hq)}', flush=True)
        return amb

    ambulances = generate_n(
        gen_ambulance,
        n=AMBULANCES_COUNT
    )
    MC = ManagementCenter(policemen)
    AHQ = AmbulanceHeadquarter(ambulances)
    print('', flush=True)
    return [
        *policemen,
        *ambulances,
        MC,
        AHQ,
    ], police_outposts, ambulance_hq


def add_unit(sim_manager):
    from smart_intervention.globals import CityMap
    from smart_intervention.events.intervention_event import InterventionEvent
    from smart_intervention.models.actors.policeman.policeman import Policeman
    from smart_intervention.models.actors.ambulance.ambulance import Ambulance

    actor_type = input('Pick actor type:\n\tp => Policeman\n\ta => Ambulance\n')
    if actor_type not in ['a', 'p']:
        print('ERROR: Invalid actor type chosen', flush=True)
        return

    eff = input(
        'Pick actors efficiency - floating point (0-1) suggested:\n')
    try:
        eff = float(eff)
    except ValueError:
        print(f'Invalid value chosen as actors efficiency!: {eff}', flush=True)
        return
    actor = None
    if actor_type == 'p':
        outposts = sim_manager.police_outposts

        location_id = input(f'Pick a police outpost from this list:\n\t{id_list(outposts)}\n')
        outpost = validate_and_get_user_choice(outposts, location_id)

        print(f'Policeman inserted!\n\tOutpost: {id(outpost)}\n\tEfficiency: {eff}\n', flush=True)
        actor = Policeman(
            purpose=PolicemanPurpose.IDLE,
            location=outpost,
            efficiency=eff,
            policeman_hq=outpost
        )
    elif actor_type == 'a':
        a_hq = sim_manager.ambulance_hq
        print(f'Ambulance inserted!\n\tHeadquarter: {id(a_hq)}\n\tEfficiency: {eff}\n', flush=True)
        actor = Ambulance(
            purpose=AmbulancePurpose.IDLE,
            location=a_hq,
            efficiency=eff,
            ambulance_hq=a_hq
        )
    if actor:
        sim_manager.add_actor(actor)


def validate_and_get_user_choice(list, id_choice):
    try:
        id_choice = int(id_choice) - 1
    except ValueError:
        raise RuntimeError('Non-numeric table id given')

    if id_choice not in range(0, len(list)):
        raise RuntimeError('ERROR: Chosen index out of range')

    return list[id_choice]


def id_list(iterable):
    return '\n\t'.join([f'{idx + 1}: {id(item)}' for idx, item in enumerate(iterable)])


def get_route_from_user():
    from smart_intervention.globals import CityMap
    locations = CityMap.get_locations()

    route = []

    pick_location_command = f'Pick a location from this list, or "f" to finish creating route:\n\t{id_list(locations)}\n'

    location_id = input(pick_location_command)
    while location_id != 'f':
        try:
            location = validate_and_get_user_choice(locations, location_id)
        except RuntimeError:
            if location_id == 'f':
                break
            else:
                return

        route.append(location)
        location_id = input(pick_location_command)

    return route


def send_unit_to_patrol(sim_manager):
    policemen = sim_manager.get_policemen()
    available_policemen = [policeman for policeman in policemen if policeman.is_free()]
    if not available_policemen:
        print('No policemen are available for patrol. Aborting...', flush=True)

    policemen_ids = id_list(policemen)
    policeman_id = input(f'Pick a policeman id from this list:\n\t{policemen_ids}\n')
    try:
        policeman = validate_and_get_user_choice(available_policemen, policeman_id)
    except RuntimeError as r_err:
        print(r_err, flush=True)
        return
    route = get_route_from_user()
    if not route:
        print('ERROR: Empty route not allowed. Aborting...', flush=True)
        return

    policeman.patrol_route = route
    policeman.re_purpose(PolicemanPurpose.PATROL)


def create_intervention(sim_manager):
    from smart_intervention.globals import CityMap
    from smart_intervention.events.intervention_event import InterventionEvent
    locations = CityMap.get_locations()
    forbidden_locations = [*sim_manager.police_outposts, sim_manager.ambulance_hq]
    free_locations = [
        location for location in locations
        if not location.intervention_event and location not in forbidden_locations
    ]
    if not free_locations:
        print('All of locations have an event, unable to create one. Aborting...', flush=True)

    autogen = input('Do you want to auto generate event? y/n\n')
    if autogen == 'y':
        danger = round(random(), 2)
        health_index = round(random() * 10, 0)
        location = pick_random(free_locations)

        print(f'Generated event: \n\tLocation: {id(location)}\n\tHealth: {health_index}\n\tDanger: {danger}\n', flush=True)
    else:
        location_id = input(f'Pick a location from this list:\n\t{id_list(free_locations)}\n')
        try:
            location = validate_and_get_user_choice(free_locations, location_id)
        except RuntimeError:
            print('ERROR: Invalid location chosen', flush=True)
            return

        danger = input(
            'Pick danger index (floating point 0-1), which indicates how likely the event is to break out into gunfight:\n')
        try:
            danger = float(danger)
        except ValueError:
            print(f'Invalid value chosen as danger level!: {danger}', flush=True)
            return

        health_index = input(
            'Pick events health index (number), which indicates how difficult it is for policemen to finish:\n')
        try:
            health_index = float(health_index)
        except ValueError:
            print(f'Invalid value chosen as health_index level!: {health_index}', flush=True)
            return

    location.intervention_event = InterventionEvent(danger, health_index, location)


def send_unit_back_to_hq(sim_manager):
    patroling_policemen = [
        actor for actor in sim_manager.actors
        if hasattr(actor, 'purpose') and actor.purpose == PolicemanPurpose.PATROL
    ]
    if not patroling_policemen:
        print('No currently patroling policemen! Aborting...', flush=True)
        return
    policeman_id = input(f'Pick a patroling policeman from this list:\n\t{id_list(patroling_policemen)}\n')
    policeman = validate_and_get_user_choice(patroling_policemen, policeman_id)
    print(f'Sending Policeman #{id(policeman)} back to headquarter!', flush=True)

    policeman.route_with_purpose(policeman.policeman_hq, PolicemanPurpose.RETURNING_TO_HQ)


def interpret_command(input, sim_manager):
    inp_strip = input.strip()
    if inp_strip == 'ev':
        create_intervention(sim_manager)
    elif inp_strip == 'au':
        add_unit(sim_manager)
    elif inp_strip == 's':
        print('Performing simulation step...', flush=True)
        sim_manager.do_tick()
    elif inp_strip == 'pt':
        send_unit_to_patrol(sim_manager)
    elif inp_strip == 'rc':
        send_unit_back_to_hq(sim_manager)
    else:
        print('Unable to recognise command, please try again.', flush=True)


def random_route():
    from smart_intervention.globals import CityMap
    locations = CityMap.get_locations()
    route_length = pick_random(range(1, len(locations) - 3))
    route = []
    for i in range(route_length):
        if i == 0:
            route.append(pick_random(locations))
        else:
            next_locations_candidates = [
                location for location in locations
                if location != route[i - 1]
            ]
            route.append(pick_random(next_locations_candidates))
    return route


def send_random_unit_to_patrol(sim_manager):
    from smart_intervention.models.actors.management_center.management_center_resource_monitor import ResourceState
    available_policemen = sim_manager.get_actor_by_type('ManagementCenter')._resource_monitor._units[ResourceState.AVAILABLE]
    # available_policemen = [policeman for policeman in policemen if policeman.purpose == PolicemanPurpose.IDLE]

    if len(available_policemen) > 0 and random_decision(0.05):
        policeman = pick_random(available_policemen)
        rand_route = random_route()
        policeman.patrol_route = rand_route
        policeman.re_purpose(PolicemanPurpose.PATROL)
        print(f'Sent unit #{id(policeman)} to patrol! Route: {[id(location) for location in rand_route]} ', flush=True)


def insert_random_intervention(sim_manager):
    from smart_intervention.globals import CityMap
    from smart_intervention.events.intervention_event import InterventionEvent

    def generate_random_intervention():
        locations = CityMap.get_locations()
        forbidden_locations = [*sim_manager.police_outposts, sim_manager.ambulance_hq]
        free_locations = [
            location for location in locations
            if not location.intervention_event and location not in forbidden_locations
        ]
        if not free_locations:
            return
        danger = round(random(), 2)
        health_index = random() * 10
        location = pick_random(free_locations)
        location.intervention_event = InterventionEvent(danger, health_index, location)
        print(f'Generated event: Location: {id(location)}, Health: {health_index}, Danger: {danger}', flush=True)


    active_interventions = len(CityMap.get_interventions())
    if active_interventions >= 2:
        return
    elif active_interventions == 1 and random_decision(0.2):
        generate_random_intervention()
    elif active_interventions == 0 and random_decision(0.4):
        generate_random_intervention()


def send_randomly_back_unit_to_hq(sim_manager):
    patroling_policemen = [
        actor for actor in sim_manager.actors
        if hasattr(actor, 'purpose') and actor.purpose == PolicemanPurpose.PATROL
    ]
    if not patroling_policemen:
        return

    if random_decision(0.01):
        policeman = pick_random(patroling_policemen)
        print(f'Sending Policeman #{id(policeman)} back to headquarter!', flush=True)

        policeman.route_with_purpose(policeman.policeman_hq, PolicemanPurpose.RETURNING_TO_HQ)


def do_simple_simulation(random_simulation=False):
    initial_actors, police_outposts, ambulance_hq = generate_environment_and_actors()
    sim_manager = SimulationManager(police_outposts, ambulance_hq, initial_actors)
    if random_simulation:
        while True:
            # print('Performing simulation step...', flush=True)
            sim_manager.do_tick()
            insert_random_intervention(sim_manager)
            send_random_unit_to_patrol(sim_manager)
            send_randomly_back_unit_to_hq(sim_manager)

    else:
        inp = input(COMMAND_INSTRUCTION)
        interpret_command(inp, sim_manager)
        while inp != 'exit':
            inp = input(COMMAND_INSTRUCTION)
            interpret_command(inp, sim_manager)

        print('Terminating...', flush=True)


if __name__ == '__main__':
    do_simple_simulation(random_simulation=True)
