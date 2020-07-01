import itertools

import networkx as nx

from networkx.utils import py_random_state


@py_random_state(2)
def gnp_random_graph(nodes, p, seed=None, directed=False):
    n = len(nodes)
    if directed:
        permutations = itertools.permutations(range(n), 2)
        edges = [(nodes[permutation[0]], nodes[permutation[1]]) for permutation in permutations]
        G = nx.DiGraph()
    else:
        combinations = itertools.combinations(range(n), 2)
        edges = [(nodes[combination[0]], nodes[combination[1]]) for combination in combinations]
        G = nx.Graph()
    G.add_nodes_from(nodes)
    if p <= 0:
        return G
    if p >= 1:
        return nx.complete_graph(n, create_using=G)

    for e in edges:
        if seed.random() < p:
            G.add_edge(*e)
    return G


def pairwise_nodes(n):
    a, b = itertools.tee(n)
    next(b, None)
    return zip(a, b)


def path_graph(n):
    G = nx.empty_graph(n)
    G.add_edges_from(pairwise_nodes(n))
    return G
