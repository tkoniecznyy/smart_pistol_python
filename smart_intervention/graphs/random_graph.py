import math

import networkx as nx

from networkx.utils import py_random_state


@py_random_state(2)
def gnp_directed_graph(nodes, p, seed=None):
    n = len(nodes)
    w = -1
    lp = math.log(1.0 - p)

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    # Nodes in graph are from 0,n-1 (start with v as the first node index).
    v = 0
    while v < n:
        lr = math.log(1.0 - seed.random())
        w = w + 1 + int(lr / lp)
        if v == w:  # avoid self loops
            w = w + 1
        while v < n <= w:
            w = w - n
            v = v + 1
            if v == w:  # avoid self loops
                w = w + 1
        if v < n:
            G.add_edge(nodes[v], nodes[w])
    return G
