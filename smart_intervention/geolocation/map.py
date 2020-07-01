from itertools import chain

import networkx as nx
from .location import Location


class RoutingError(Exception):
    pass


class Map:
    """
    Class which can give directions, and manages related city graph
    """

    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def route(self, source: Location, target: Location):
        if self.graph.has_node(source) and self.graph.has_node(target):
            try:
                return nx.shortest_path(self.graph, source, target)
            except nx.exception.NetworkXNoPath:
                raise RoutingError('No path found between source and target')
        else:
            raise RoutingError('Route for non-existing location has been requested!')

    def all_actors(self):
        return chain.from_iterable(map(lambda x: x.actors, self.graph.nodes))

    def get_distance(self, a, b):
        return nx.shortest_path_length(self.graph, a, b)

    def get_interventions(self):
        return [
            node.intervention_event
            for node in self.graph.nodes
            if node.intervention_event is not None
        ]

    def get_locations(self):
        return list(self.graph.nodes)
