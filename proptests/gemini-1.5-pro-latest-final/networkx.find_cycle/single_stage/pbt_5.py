from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs, parameters, and edge cases
@given(st.data())
def test_networkx_find_cycle(data):
    # Generate graph type and number of nodes
    graph_type = data.draw(st.sampled_from([nx.Graph, nx.DiGraph]))
    num_nodes = data.draw(st.integers(min_value=0, max_value=100))
    
    # Create graph with varying edge density
    p_edge = data.draw(st.floats(min_value=0, max_value=1))
    graph = graph_type()
    graph.add_nodes_from(range(num_nodes))
    for u in range(num_nodes):
        for v in range(u + 1, num_nodes):
            if data.draw(st.booleans(p=p_edge)):
                if graph_type == nx.DiGraph:
                    # For directed graphs, randomly choose direction
                    direction = data.draw(st.booleans())
                    graph.add_edge(u, v if direction else v, u) 
                else:
                    graph.add_edge(u, v)

    # Generate source and orientation parameters
    source = data.draw(st.one_of(st.sampled_from(graph.nodes()), st.none()))
    orientation = None
    if graph_type == nx.DiGraph:
        orientation = data.draw(st.sampled_from([None, 'original', 'reverse', 'ignore']))

    # Test find_cycle and check properties
    try:
        cycle = nx.find_cycle(graph, source, orientation)
        assert isinstance(cycle, list)
        # Check edge format based on graph type
        if graph_type == nx.Graph:
            assert all(len(edge) == 2 and isinstance(edge[0], int) and isinstance(edge[1], int) for edge in cycle)
        else:
            assert all(len(edge) in [2, 3] and isinstance(edge[0], int) and isinstance(edge[1], int) for edge in cycle)
            if orientation is not None:
                assert all(len(edge) == 3 and edge[2] in ['forward', 'reverse'] for edge in cycle)
        # Verify that the edges form a cycle
        assert all(edge[1] in [cycle[(i + 1) % len(cycle)][0] for i in range(len(cycle))])
    except nx.NetworkXNoCycle:
        pass  # Expected behavior if no cycle exists

# End program