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
