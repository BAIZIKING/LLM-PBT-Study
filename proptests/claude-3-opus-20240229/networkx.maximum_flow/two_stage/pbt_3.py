from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_flow_value_non_negative(data):
    G = nx.DiGraph()
    nodes = data.draw(st.lists(st.integers(), min_size=2, max_size=100, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True))
    capacities = data.draw(st.dictionaries(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), st.floats(min_value=0, max_value=1000), min_size=len(edges), max_size=len(edges)))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_edge_attributes(G, capacities, 'capacity')
    _s, _t = data.draw(st.lists(st.sampled_from(nodes), min_size=2, max_size=2, unique=True))
    flow_value, _ = nx.maximum_flow(G, _s, _t)
    assert flow_value >= 0

@given(st.data())
def test_flow_value_less_than_total_capacity(data):
    G = nx.DiGraph()
    nodes = data.draw(st.lists(st.integers(), min_size=2, max_size=100, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True))
    capacities = data.draw(st.dictionaries(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), st.floats(min_value=0, max_value=1000), min_size=len(edges), max_size=len(edges)))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_edge_attributes(G, capacities, 'capacity')
    _s, _t = data.draw(st.lists(st.sampled_from(nodes), min_size=2, max_size=2, unique=True))
    flow_value, _ = nx.maximum_flow(G, _s, _t)
    total_capacity = sum(capacities.get((_s, v), 0) for v in G.neighbors(_s))
    assert flow_value <= total_capacity

@given(st.data())
def test_flow_dict_capacity_constraints(data):
    G = nx.DiGraph()
    nodes = data.draw(st.lists(st.integers(), min_size=2, max_size=100, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True))
    capacities = data.draw(st.dictionaries(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), st.floats(min_value=0, max_value=1000), min_size=len(edges), max_size=len(edges)))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_edge_attributes(G, capacities, 'capacity')
    _s, _t = data.draw(st.lists(st.sampled_from(nodes), min_size=2, max_size=2, unique=True))
    _, flow_dict = nx.maximum_flow(G, _s, _t)
    for u, v in G.edges():
        assert 0 <= flow_dict[u][v] <= capacities.get((u, v), 0)

@given(st.data())
def test_flow_conservation(data):
    G = nx.DiGraph()
    nodes = data.draw(st.lists(st.integers(), min_size=2, max_size=100, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True))
    capacities = data.draw(st.dictionaries(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), st.floats(min_value=0, max_value=1000), min_size=len(edges), max_size=len(edges)))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_edge_attributes(G, capacities, 'capacity')
    _s, _t = data.draw(st.lists(st.sampled_from(nodes), min_size=2, max_size=2, unique=True))
    _, flow_dict = nx.maximum_flow(G, _s, _t)
    for u in G.nodes():
        if u != _s and u != _t:
            assert sum(flow_dict[u][v] for v in G.neighbors(u)) == sum(flow_dict[v][u] for v in G.predecessors(u))

@given(st.data())
def test_maximum_flow_value_achieved(data):
    G = nx.DiGraph()
    nodes = data.draw(st.lists(st.integers(), min_size=2, max_size=100, unique=True))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True))
    capacities = data.draw(st.dictionaries(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), st.floats(min_value=0, max_value=1000), min_size=len(edges), max_size=len(edges)))
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_edge_attributes(G, capacities, 'capacity')
    _s, _t = data.draw(st.lists(st.sampled_from(nodes), min_size=2, max_size=2, unique=True))
    flow_value, flow_dict = nx.maximum_flow(G, _s, _t)
    if flow_value == sum(capacities.get((_s, v), 0) for v in G.neighbors(_s)):
        R = nx.DiGraph(flow_dict)
        assert not nx.has_path(R, _s, _t)
# End program