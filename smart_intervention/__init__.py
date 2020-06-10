__version__ = '0.1.0'

import smart_intervention.graphs as graphs
from smart_intervention.geolocation.location import Location
from smart_intervention.geolocation.map import Map
from smart_intervention.models.actors.ambulance.ambulance import Ambulance
from smart_intervention.models.actors.ambulance_headquarter.ambulance_headquarter import AmbulanceHeadquarter
from smart_intervention.models.actors.management_center.management_center import ManagementCenter

from smart_intervention.models.simulation_manager import SimulationManager
from smart_intervention.models.actors.policeman.policeman import Policeman
from smart_intervention.notifications.notification_store import NotificationStore
from smart_intervention.simulation_variable_type import SimulationVariableType
from smart_intervention.utils.iter_utils import pick_random, generate_n
from random import random

POLICEMEN_COUNT = 10
AMBULANCES_COUNT = 3
NODE_COUNT = 10
COMMAND_INSTRUCTION = 'Loop stopped, please enter command: s => step, exit => terminate program'
nodes = generate_n(lambda _: Location(), n=NODE_COUNT)
city_graph = graphs.gnp_directed_graph(nodes, .2)
Notifications = NotificationStore()  # TODO: Rename that. This collides with notifications passed around as objects
CityMap = Map(city_graph)
SimulationVariables = {
    SimulationVariableType.GUNFIGHT_BREAKOUT_RATE: 0.3,
    SimulationVariableType.REDUNDANCY_OF_MANPOWER: 0.1,
}


def generate_environment_and_actors():
    police_outposts = [pick_random(city_graph.nodes), pick_random(city_graph.nodes)]
    ambulance_hq = pick_random(city_graph.nodes)
    policemen = generate_n(
        lambda _: Policeman(
            purpose=Policeman.PolicemanPurpose.IDLE,
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


def do_simple_simulation():
    initial_actors, outposts, hq = generate_environment_and_actors()
    sim_manager = SimulationManager(initial_actors)

    inp = input(COMMAND_INSTRUCTION)
    while inp != 'exit':
        sim_manager.do_tick()
        inp = input(COMMAND_INSTRUCTION)

    print('Terminating...')


if __name__ == '__main__':
    do_simple_simulation()
