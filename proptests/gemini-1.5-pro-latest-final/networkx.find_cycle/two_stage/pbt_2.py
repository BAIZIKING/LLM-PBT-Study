from hypothesis import given, strategies as st
import networkx

# Define strategies for graph generation
def graph_strategy():
    # Limit size due to potential complexity
    return st.graphs(min_size=2, max_size=15, edge_strategy=st.tuples(st.integers(), st.integers()))

def orientation_strategy():
    return st.sampled_from([None, 'original', 'reverse', 'ignore']) 

@given(graph=graph_strategy(), orientation=orientation_strategy())
def test_networkx_find_cycle_cycle_property(graph, orientation):
    # Only execute if a cycle exists (avoiding NetworkXNoCycle exception)
    if networkx.is_directed_acyclic_graph(graph):
        return

    cycle = networkx.find_cycle(graph, orientation=orientation)
    start_node = cycle[0][0]
    current_node = start_node
    for u, v, *direction in cycle:
        assert (u, v) in graph.edges or (v, u) in graph.edges  # Checking for edge existence in undirected case
        current_node = v
    assert current_node == start_node  # Verify we return to the start

@given(graph=graph_strategy(), orientation=orientation_strategy())
def test_networkx_find_cycle_containment_property(graph, orientation):
    # Only execute if a cycle exists (avoiding NetworkXNoCycle exception)
    if networkx.is_directed_acyclic_graph(graph):
        return

    cycle = networkx.find_cycle(graph, orientation=orientation)
    for u, v, *direction in cycle:
        assert (u, v) in graph.edges or (v, u) in graph.edges 

@given(graph=st.directed_graphs(min_size=2, max_size=15, edge_strategy=st.tuples(st.integers(), st.integers())))
def test_networkx_find_cycle_directionality_original(graph):
    # Only test directed graphs and only if a cycle exists
    if networkx.is_directed_acyclic_graph(graph):
        return

    cycle = networkx.find_cycle(graph, orientation='original')
    for u, v, direction in cycle:
        assert graph.has_edge(u, v)  # Edge direction must match original direction

@given(graph=graph_strategy(), orientation=orientation_strategy())
def test_networkx_find_cycle_path_length(graph, orientation):
    # Only execute if a cycle exists (avoiding NetworkXNoCycle exception)
    if networkx.is_directed_acyclic_graph(graph):
        return
    cycle = networkx.find_cycle(graph, orientation=orientation)
    assert len(cycle) >= 2

@given(graph=st.graphs(min_size=2, max_size=15, edge_strategy=st.tuples(st.integers(), st.integers())))  # Simple graphs
def test_networkx_find_cycle_uniqueness_edges(graph):
     # Only execute if a cycle exists (avoiding NetworkXNoCycle exception)
    if networkx.is_directed_acyclic_graph(graph):
        return

    cycle = networkx.find_cycle(graph)
    edges = [(u, v) for u, v, *direction in cycle]  # Extract edges ignoring direction
    assert len(set(edges)) == len(edges)  # Check for uniqueness using set

# End program