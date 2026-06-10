from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cycle_valid_cycle(data):
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    cycle = nx.find_cycle(G)
    for i in range(len(cycle)):
        assert cycle[i][1] == cycle[(i+1) % len(cycle)][0]

@given(st.data())
def test_find_cycle_no_duplicates(data):
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    cycle = nx.find_cycle(G)
    assert len(set(cycle)) == len(cycle)

@given(st.data())
def test_find_cycle_acyclic_graph(data):
    nodes = data.draw(st.sets(st.integers(), min_size=1, max_size=100))
    edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), max_size=len(nodes)-1))
    G = nx.DiGraph(edges)
    try:
        nx.find_cycle(G)
        assert False
    except nx.NetworkXNoCycle:
        assert True

@given(st.data())
def test_find_cycle_original_orientation(data):
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    cycle = nx.find_cycle(G, orientation='original')
    for u, v, direction in cycle:
        assert direction == 'forward'

@given(st.data())
def test_find_cycle_reverse_orientation(data):
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    cycle = nx.find_cycle(G, orientation='reverse')
    for u, v, direction in cycle:
        assert direction == 'reverse'
# End program