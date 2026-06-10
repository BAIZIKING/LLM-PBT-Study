from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs, capacities, and flow functions to test networkx.maximum_flow comprehensively.
@given(st.data())
def test_networkx_maximum_flow(data):
    # Generate graph type and node/edge counts
    graph_type = data.draw(st.sampled_from([nx.DiGraph, nx.MultiDiGraph]))
    num_nodes = data.draw(st.integers(min_value=2, max_value=20))
    num_edges = data.draw(st.integers(min_value=1, max_value=num_nodes*(num_nodes-1)))

    # Create graph and add edges with capacities
    graph = graph_type()
    for _ in range(num_edges):
        u, v = data.draw(st.tuples(st.integers(max_value=num_nodes-1), st.integers(max_value=num_nodes-1)))
        capacity = data.draw(st.one_of(st.floats(min_value=1), st.just(float('inf'))))
        graph.add_edge(u, v, capacity=capacity)

    # Select source and sink nodes
    source, sink = data.draw(st.tuples(st.sampled_from(graph.nodes), st.sampled_from(graph.nodes)))

    # Choose flow function
    flow_func = data.draw(st.one_of(st.none(), st.just(nx.shortest_augmenting_path)))

    # Test cases based on graph type
    if isinstance(graph, nx.MultiDiGraph):
        with pytest.raises(nx.NetworkXError):
            nx.maximum_flow(graph, source, sink, flow_func=flow_func)
    else:
        try:
            flow_value, flow_dict = nx.maximum_flow(graph, source, sink, flow_func=flow_func)
            # Check flow value and conservation
            assert flow_value >= 0
            assert sum(flow_dict[source].values()) == flow_value == -sum(flow_dict[sink].values())
            for node in graph.nodes:
                if node not in (source, sink):
                    assert sum(inflow for inflow in flow_dict[node].values()) == sum(outflow for outflow in flow_dict.get(node, {}).values())
            # Check capacity constraints
            for u, v in graph.edges:
                assert 0 <= flow_dict[u][v] <= graph[u][v]['capacity']
        except nx.NetworkXUnbounded:
            # Check if a path with infinite capacity exists
            assert any(all(graph[u][v]['capacity'] == float('inf') for u, v in path)
                       for path in nx.all_simple_paths(graph, source, sink))

# End program