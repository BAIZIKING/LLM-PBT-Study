from hypothesis import given, strategies as st, settings
from hypothesis.strategies import lists, tuples, integers, none, sampled_from
from math import isnan
import networkx as nx

@given(st.graphs(directed=True, max_nodes=100))
@settings(max_examples=500)
def test_networkx_find_cycle_property1(G):
    try:
        nx.find_cycle(G)
    except nx.NetworkXNoCycle:
        assert nx.is_directed_acyclic_graph(G)

@given(st.graphs(directed=True, max_nodes=100))
@settings(max_examples=500)
def test_networkx_find_cycle_property2(G):
    try:
        cycle = nx.find_cycle(G)
        for i in range(len(cycle) - 1):
            assert G.has_edge(cycle[i][0], cycle[i][1])
        assert G.has_edge(cycle[-1][0], cycle[0][0])
    except nx.NetworkXNoCycle:
        pass

@given(st.graphs(directed=True, max_nodes=100), sampled_from(['original', 'reverse', 'ignore', None]))
@settings(max_examples=200)
def test_networkx_find_cycle_property3(G, orientation):
    try:
        cycle = nx.find_cycle(G, orientation=orientation)
        if orientation == 'original':
            for u, v, *_ in cycle:
                assert G.has_edge(u, v)
        elif orientation == 'reverse':
            for u, v, *_ in cycle:
                assert G.has_edge(v, u)
    except nx.NetworkXNoCycle:
        pass

@given(st.graphs(directed=True, max_nodes=100))
@settings(max_examples=500)
def test_networkx_find_cycle_property4(G):
    try:
        cycle = nx.find_cycle(G, orientation='ignore')
        H = nx.Graph(G)
        for i in range(len(cycle) - 1):
            assert H.has_edge(cycle[i][0], cycle[i][1])
        assert H.has_edge(cycle[-1][0], cycle[0][0])
    except nx.NetworkXNoCycle:
        pass
# End program