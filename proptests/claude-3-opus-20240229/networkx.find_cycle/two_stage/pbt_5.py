from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cycle_forms_valid_cycle(data):
    nodes = data.draw(st.sets(elements=st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(elements=st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    cycle = nx.find_cycle(G)
    for i in range(len(cycle)):
        assert cycle[i][1] == cycle[(i+1) % len(cycle)][0]

@given(st.data())
def test_find_cycle_raises_exception_on_acyclic_graph(data):
    nodes = data.draw(st.sets(elements=st.integers(), min_size=1, max_size=100))
    edges = data.draw(st.sets(elements=st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), max_size=len(nodes)-1))
    G = nx.DiGraph(edges)
    try:
        nx.find_cycle(G)
        assert False
    except nx.NetworkXNoCycle:
        pass

@given(st.data())
def test_find_cycle_includes_source_node(data):
    nodes = data.draw(st.sets(elements=st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(elements=st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    source = data.draw(st.sampled_from(list(nodes)))
    cycle = nx.find_cycle(G, source)
    assert source in [e[0] for e in cycle] or source in [e[1] for e in cycle]

@given(st.data())
def test_find_cycle_respects_original_edge_orientation(data):
    nodes = data.draw(st.sets(elements=st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(elements=st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    cycle = nx.find_cycle(G, orientation='original')
    for u, v, direction in cycle:
        assert G.has_edge(u, v)

@given(st.data())
def test_find_cycle_reverses_edge_orientation(data):
    nodes = data.draw(st.sets(elements=st.integers(), min_size=3, max_size=100))
    edges = data.draw(st.sets(elements=st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=len(nodes), max_size=len(nodes)*2))
    G = nx.DiGraph(edges)
    cycle = nx.find_cycle(G, orientation='reverse')
    for u, v, direction in cycle:
        assert G.has_edge(v, u)
# End program