from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs and tests find_cycle behavior
@given(
    graph_type=st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]),
    num_nodes=st.integers(min_value=0, max_value=100),
    edge_density=st.floats(min_value=0.0, max_value=1.0),
    source=st.one_of(st.none(), st.integers()),
    orientation=st.sampled_from([None, 'original', 'reverse', 'ignore'])
)
def test_networkx_find_cycle(graph_type, num_nodes, edge_density, source, orientation):
    # Generate a random graph
    graph = graph_type()
    for i in range(num_nodes):
        graph.add_node(i)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if st.random().random() < edge_density:
                graph.add_edge(i, j)

    # Test find_cycle
    try:
        cycle = nx.find_cycle(graph, source=source, orientation=orientation)
        # Check cycle properties
        assert cycle[0][0] == cycle[-1][-2]  # Cycle starts and ends at the same node
        assert all(edge in graph.edges for edge in cycle)  # All edges in the cycle exist in the graph
        # Add more assertions to check orientation and other properties
    except nx.NetworkXNoCycle:
        assert not nx.is_directed_acyclic_graph(graph)  # Check if the graph actually has no cycle

# End program