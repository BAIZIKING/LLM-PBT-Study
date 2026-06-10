from hypothesis import given, strategies as st
import networkx as nx

# Summary: The generation strategy aims to create a diverse set of inputs for testing `networkx.find_cycle`.
# It generates random graphs with varying structures (directed/undirected, with/without multi-edges), sizes, and densities.
# The strategy also considers edge cases such as empty graphs, graphs with self-loops, and graphs with isolated nodes.
# Additionally, it generates different values for the `source` and `orientation` parameters to cover various traversal starting points and edge direction handling scenarios.
@given(st.data())
def test_networkx_find_cycle(data):
    # Generate graph type: directed or undirected
    graph_type = data.draw(st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]))

    # Generate graph size and density
    num_nodes = data.draw(st.integers(min_value=0, max_value=100))  # Adjust max_value for larger graphs
    p = data.draw(st.floats(min_value=0.0, max_value=1.0))  # Probability of edge creation

    # Generate graph with specified type, size, and density
    G = data.draw(st.graphs(graph_type, num_nodes, p))

    # Generate optional source node or list of nodes
    source_strategy = st.one_of(st.none(), st.integers(min_value=0, max_value=num_nodes - 1),
                                 st.lists(st.integers(min_value=0, max_value=num_nodes - 1), min_size=1, max_size=num_nodes))
    source = data.draw(source_strategy)

    # Generate orientation parameter: None, 'original', 'reverse', or 'ignore'
    orientation = data.draw(st.sampled_from([None, 'original', 'reverse', 'ignore']))

    # Check properties based on the API documentation:

    # 1. If a cycle is found, the returned list should contain edges that form a closed loop.
    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
        # Verify that the cycle starts and ends at the same node
        assert cycle[0][0] == cycle[-1][-2]  # Adjust indices for multigraphs if needed
        # Verify that each consecutive pair of edges in the cycle share a common node
        for i in range(len(cycle) - 1):
            assert cycle[i][-2] == cycle[i + 1][0]  # Adjust indices for multigraphs if needed
    except nx.NetworkXNoCycle:
        # 2. If no cycle is found, a NetworkXNoCycle exception should be raised.
        pass

# End program