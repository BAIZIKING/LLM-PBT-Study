from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cycle_acyclic_graph(data):
    # Generate an acyclic graph
    nodes = data.draw(st.sets(st.integers(), min_size=1, max_size=100))
    edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), max_size=len(nodes) - 1))
    G = nx.DiGraph(edges)
    
    # Check that the function raises a NetworkXNoCycle exception
    try:
        nx.find_cycle(G)
        assert False, "Expected NetworkXNoCycle exception"
    except nx.NetworkXNoCycle:
        pass

@given(st.data())
def test_find_cycle_valid_cycle(data):
    # Generate a graph with a cycle
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    cycle_nodes = data.draw(st.lists(st.sampled_from(nodes), min_size=3, max_size=len(nodes), unique=True))
    cycle_edges = list(zip(cycle_nodes, cycle_nodes[1:] + [cycle_nodes[0]]))
    other_edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), max_size=len(nodes)))
    G = nx.DiGraph(cycle_edges + list(other_edges))
    
    # Check that the returned cycle is valid
    cycle = nx.find_cycle(G)
    assert set(cycle) <= set(G.edges), "Returned cycle contains edges not present in the graph"
    assert len(set(node for edge in cycle for node in edge)) == len(cycle), "Returned cycle is not a valid cycle"

@given(st.data())
def test_find_cycle_original_orientation(data):
    # Generate a graph with a directed cycle
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    cycle_nodes = data.draw(st.lists(st.sampled_from(nodes), min_size=3, max_size=len(nodes), unique=True))
    cycle_edges = list(zip(cycle_nodes, cycle_nodes[1:] + [cycle_nodes[0]]))
    other_edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), max_size=len(nodes)))
    G = nx.DiGraph(cycle_edges + list(other_edges))
    
    # Check that the returned cycle respects the original edge orientations
    cycle = nx.find_cycle(G, orientation="original")
    for i in range(len(cycle) - 1):
        assert cycle[i][1] == cycle[i + 1][0], "Returned cycle does not respect original edge orientations"
    assert cycle[-1][1] == cycle[0][0], "Returned cycle does not respect original edge orientations"

@given(st.data())
def test_find_cycle_reverse_orientation(data):
    # Generate a graph with a directed cycle
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    cycle_nodes = data.draw(st.lists(st.sampled_from(nodes), min_size=3, max_size=len(nodes), unique=True))
    cycle_edges = list(zip(cycle_nodes, cycle_nodes[1:] + [cycle_nodes[0]]))
    other_edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), max_size=len(nodes)))
    G = nx.DiGraph(cycle_edges + list(other_edges))
    
    # Check that the returned cycle traverses edges in the reverse direction
    cycle = nx.find_cycle(G, orientation="reverse")
    for i in range(len(cycle) - 1):
        assert cycle[i][0] == cycle[i + 1][1], "Returned cycle does not traverse edges in reverse direction"
    assert cycle[-1][0] == cycle[0][1], "Returned cycle does not traverse edges in reverse direction"

@given(st.data())
def test_find_cycle_ignore_orientation(data):
    # Generate a graph with an undirected cycle
    nodes = data.draw(st.sets(st.integers(), min_size=3, max_size=100))
    cycle_nodes = data.draw(st.lists(st.sampled_from(nodes), min_size=3, max_size=len(nodes), unique=True))
    cycle_edges = list(zip(cycle_nodes, cycle_nodes[1:] + [cycle_nodes[0]]))
    other_edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), max_size=len(nodes)))
    G = nx.Graph(cycle_edges + list(other_edges))
    
    # Check that the returned cycle ignores edge orientations
    cycle = nx.find_cycle(G, orientation="ignore")
    assert set(cycle) <= set(G.edges), "Returned cycle contains edges not present in the graph"
    assert len(set(node for edge in cycle for node in edge)) == len(cycle), "Returned cycle is not a valid cycle"
# End program