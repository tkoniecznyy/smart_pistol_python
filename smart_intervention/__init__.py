__version__ = '0.1.0'

from random import random

import smart_intervention.graphs as graphs
from smart_intervention.geolocation.location import Location
from smart_intervention.geolocation.map import Map

from smart_intervention.models.simulation_manager import SimulationManager
from smart_intervention.models.actors.policeman import Policeman
from smart_intervention.notifications.notification_store import NotificationStore
from smart_intervention.utils.iter_utils import pick_random, generate_n

POLICEMEN_COUNT = 10
NODE_COUNT = 10


notification_store = NotificationStore()
city_map = Map()

def do_simple_simulation():
    nodes = generate_n(lambda _: Location(), n=NODE_COUNT)

    graph = graphs.gnp_directed_graph(nodes, .2)
    police_outposts = [pick_random(graph.nodes), pick_random(graph.nodes)]

    policemen = generate_n(
        lambda _: Policeman(purpose=Policeman.PolicemanPurpose.IDLE, location=pick_random(police_outposts)),
        n=POLICEMEN_COUNT
    )

    initial_actors = [
        *policemen
    ]
    sim_map = Map(initial_actors, graph)
    sim_manager = SimulationManager(initial_actors)


if __name__ == '__main__':
    do_simple_simulation()
