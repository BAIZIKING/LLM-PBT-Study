from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs, capacities, and flow functions to test networkx.maximum_flow.
@given(st.data())
def test_networkx_maximum_flow(data):
    # Generate graph type and size
    graph_type = data.draw(st.sampled_from([nx.DiGraph, nx.MultiDiGraph]))
    num_nodes = data.draw(st.integers(min_value=2, max_value=20))
    num_edges = data.draw(st.integers(min_value=1, max_value=num_nodes*(num_nodes-1)))

    # Generate graph with random node labels and edge capacities
    graph = graph_type()
    graph.add_nodes_from(range(num_nodes))
    for _ in range(num_edges):
        u = data.draw(st.integers(max_value=num_nodes - 1))
        v = data.draw(st.integers(max_value=num_nodes - 1))
        capacity = data.draw(st.one_of(st.floats(allow_nan=False), st.none()))
        graph.add_edge(u, v, capacity=capacity)

    # Select source and sink nodes
    source = data.draw(st.integers(max_value=num_nodes - 1))
    sink = data.draw(st.integers(max_value=num_nodes - 1))

    # Choose flow function
    flow_func = data.draw(st.one_of(st.none(), st.just(nx.algorithms.flow.shortest_augmenting_path)))

    # Test error handling
    if type(graph) == nx.MultiDiGraph:
        with pytest.raises(nx.NetworkXError):
            nx.maximum_flow(graph, source, sink, flow_func=flow_func)
        return

    # Calculate maximum flow
    flow_value, flow_dict = nx.maximum_flow(graph, source, sink, flow_func=flow_func)

    # Verify output types
    assert isinstance(flow_value, (int, float))
    assert isinstance(flow_dict, dict)

    # Check flow conservation and capacity constraints
    for node in graph.nodes:
        if node not in (source, sink):
            inflow = sum(flow_dict[u][node] for u in graph.predecessors(node))
            outflow = sum(flow_dict[node][v] for v in graph.successors(node))
            assert inflow == outflow
        for neighbor in graph.neighbors(node):
            flow = flow_dict[node][neighbor]
            capacity = graph[node][neighbor].get('capacity', float('inf'))
            assert 0 <= flow <= capacity

    # Compare with default algorithm if flow_func is provided
    if flow_func is not None:
        default_flow_value = nx.maximum_flow(graph, source, sink)[0]
        assert flow_value == default_flow_value

# End program