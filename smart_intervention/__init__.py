__version__ = '0.1.0'


import smart_intervention.graphs as graphs
from smart_intervention.geolocation.location import Location
from smart_intervention.geolocation.map import Map

from smart_intervention.models.simulation_manager import SimulationManager
from smart_intervention.models.actors.policeman.policeman import Policeman
from smart_intervention.notifications.notification_store import NotificationStore
from smart_intervention.simulation_variable_type import SimulationVariableType
from smart_intervention.utils.iter_utils import pick_random, generate_n

POLICEMEN_COUNT = 10
NODE_COUNT = 10

nodes = generate_n(lambda _: Location(), n=NODE_COUNT)
city_graph = graphs.gnp_directed_graph(nodes, .2)
Notifications = NotificationStore()
CityMap = Map(city_graph)
SimulationVariables = {
    SimulationVariableType.GUNFIGHT_BREAKOUT_RATE: 0.3,
    SimulationVariableType.REDUNDANCY_OF_MANPOWER: 0.1,
}


def do_simple_simulation():
    police_outposts = [pick_random(city_graph.nodes), pick_random(city_graph.nodes)]

    policemen = generate_n(
        lambda _: Policeman(purpose=Policeman.PolicemanPurpose.IDLE, location=pick_random(police_outposts)),
        n=POLICEMEN_COUNT
    )

    initial_actors = [
        *policemen
    ]
    sim_manager = SimulationManager(initial_actors)


if __name__ == '__main__':
    do_simple_simulation()
