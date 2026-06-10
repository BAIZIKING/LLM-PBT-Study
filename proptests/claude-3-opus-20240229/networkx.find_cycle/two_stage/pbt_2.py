from hypothesis import given, strategies as st, settings
from hypothesis.strategies import lists, tuples
from hypothesis.extra.networkx import graph_builder
import networkx as nx

# Property 1: If the input graph is acyclic, the function should raise a NetworkXNoCycle exception
@given(graph_builder(graph_type=nx.DiGraph, min_nodes=1, max_nodes=100, min_edges=0, max_edges=1000))
@settings(max_examples=100)
def test_acyclic_graph_raises_exception(G):
    try:
        nx.find_cycle(G)
    except nx.NetworkXNoCycle:
        assert True
    else:
        assert False, "Expected NetworkXNoCycle exception for acyclic graph"

# Property 2: If a cycle is found, the returned edges should form a valid cycle in the graph
@given(graph_builder(graph_type=nx.DiGraph, min_nodes=3, max_nodes=100, min_edges=3, max_edges=1000))
@settings(max_examples=100)
def test_returned_edges_form_valid_cycle(G):
    try:
        cycle = nx.find_cycle(G)
    except nx.NetworkXNoCycle:
        pass
    else:
        assert all(u == cycle[i-1][1] for i, (u, v) in enumerate(cycle)), "Returned edges do not form a valid cycle"

# Property 3: If orientation is 'original', all edges in the cycle should respect the original direction
@given(graph_builder(graph_type=nx.DiGraph, min_nodes=3, max_nodes=100, min_edges=3, max_edges=1000))
@settings(max_examples=100)
def test_original_orientation(G):
    try:
        cycle = nx.find_cycle(G, orientation='original')
    except nx.NetworkXNoCycle:
        pass
    else:
        assert all(G.has_edge(u, v) for u, v, _ in cycle), "Returned edges do not respect original orientation"

# Property 4: If orientation is 'reverse', all edges in the cycle should be in the opposite direction
@given(graph_builder(graph_type=nx.DiGraph, min_nodes=3, max_nodes=100, min_edges=3, max_edges=1000))
@settings(max_examples=100)
def test_reverse_orientation(G):
    try:
        cycle = nx.find_cycle(G, orientation='reverse')
    except nx.NetworkXNoCycle:
        pass
    else:
        assert all(G.has_edge(v, u) for u, v, _ in cycle), "Returned edges are not in the opposite direction"

# Property 5: If orientation is 'ignore', the returned cycle may contain edges in either direction
@given(graph_builder(graph_type=nx.Graph, min_nodes=3, max_nodes=100, min_edges=3, max_edges=1000))
@settings(max_examples=100)
def test_ignore_orientation(G):
    try:
        cycle = nx.find_cycle(G, orientation='ignore')
    except nx.NetworkXNoCycle:
        pass
    else:
        assert all(G.has_edge(u, v) or G.has_edge(v, u) for u, v, _ in cycle), "Returned edges do not form a valid undirected cycle"
# End program