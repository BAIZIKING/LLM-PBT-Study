from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs and flow parameters, checks flow properties and error handling.
@given(st.data())
def test_networkx_maximum_flow(data):
    # Graph Generation
    graph_type = data.draw(st.sampled_from([nx.DiGraph, nx.Graph, nx.MultiGraph, nx.MultiDiGraph]))
    num_nodes = data.draw(st.integers(min_value=2, max_value=20))
    edge_density = data.draw(st.floats(min_value=0.1, max_value=0.9))
    graph = nx.gnp_random_graph(num_nodes, edge_density, directed=graph_type in [nx.DiGraph, nx.MultiDiGraph])

    # Add self-loops with a small probability
    for node in graph.nodes:
        if data.draw(st.booleans(p=0.2)):
            graph.add_edge(node, node)

    # Capacities and flow parameters
    for u, v in graph.edges:
        capacity = data.draw(st.integers(min_value=0))  # Allow zero capacity
        graph[u][v]['capacity'] = capacity

    source = data.draw(st.sampled_from(list(graph.nodes)))
    sink = data.draw(st.sampled_from(list(graph.nodes - {source})))
    
    # Handle expected errors
    if graph_type in [nx.MultiGraph, nx.MultiDiGraph]:
        with pytest.raises(nx.NetworkXError):
            nx.maximum_flow(graph, source, sink)
        return

    try:
        flow_value, flow_dict = nx.maximum_flow(graph, source, sink)
    except nx.NetworkXUnbounded:
        # Check if there's an infinite capacity path
        assert any(all(graph[u][v]['capacity'] == float('inf') for u, v in path) 
                   for path in nx.all_simple_paths(graph, source, sink))
        return

    # Check output types
    assert isinstance(flow_value, (int, float))
    assert isinstance(flow_dict, dict)

    # Flow conservation and capacity constraints
    for node in graph.nodes:
        if node == source:
            assert sum(flow_dict[node][v] for v in graph[node]) == flow_value
        elif node == sink:
            assert sum(-flow_dict[u][node] for u in graph.predecessors(node)) == flow_value 
        else:
            incoming_flow = sum(flow_dict[u][node] for u in graph.predecessors(node))
            outgoing_flow = sum(flow_dict[node][v] for v in graph[node])
            assert incoming_flow == outgoing_flow
        for neighbor in graph[node]:
            assert 0 <= flow_dict[node][neighbor] <= graph[node][neighbor]['capacity']

    # Flow value range
    assert flow_value >= 0

# End program