from smart_intervention.graphs.random_graph import path_graph
from smart_intervention.notifications.notification import NotificationStore
from smart_intervention.geolocation.location import Location
from smart_intervention.utils.iter_utils import generate_n
from smart_intervention.geolocation.map import Map
from smart_intervention.simulation_variable_type import SimulationVariableType

NODE_COUNT = 10
nodes = generate_n(lambda _: Location(), n=NODE_COUNT)
city_graph = path_graph(nodes)
Notifications = NotificationStore()  # TODO: Rename that. This collides with notifications passed around as objects
CityMap = Map(city_graph)
SimulationVariables = {
    SimulationVariableType.GUNFIGHT_BREAKOUT_RATE: 0.3,
    SimulationVariableType.REDUNDANCY_OF_MANPOWER: 0.1,
}
