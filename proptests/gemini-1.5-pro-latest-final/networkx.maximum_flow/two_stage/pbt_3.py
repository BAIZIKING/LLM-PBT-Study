from hypothesis import given, strategies as st
import networkx as nx

# Define a strategy for generating valid NetworkX DiGraphs with capacities
def graph_strategy():
    # Generate a reasonable range of nodes and edges to avoid overflow
    num_nodes = st.integers(min_value=2, max_value=100)
    num_edges = st.integers(min_value=1, max_value=200)

    # Generate edges with capacities
    edges = st.tuples(
        st.integers(min_value=0, max_value=num_nodes - 1),
        st.integers(min_value=0, max_value=num_nodes - 1),
        st.integers(min_value=1, max_value=100),  # Capacity range
    )

    return st.builds(
        nx.DiGraph,
        st.tuples(edges),
        num_nodes=num_nodes,
    )

# Define a strategy for source and sink nodes within the graph
def source_sink_strategy(graph):
    nodes = list(graph.nodes)
    return st.tuples(st.sampled_from(nodes), st.sampled_from(nodes))


@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_networkx_maximum_flow_conservation(graph, source_sink):
    source, sink = source_sink
    flow_value, flow_dict = nx.maximum_flow(graph, source, sink)

    # Check flow conservation for each node except source and sink
    for node in graph.nodes:
        if node != source and node != sink:
            incoming_flow = sum(flow_dict[u][node] for u in graph.predecessors(node))
            outgoing_flow = sum(flow_dict[node][v] for v in graph.successors(node))
            assert incoming_flow == outgoing_flow


@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_networkx_maximum_flow_capacity_constraints(graph, source_sink):
    source, sink = source_sink
    _, flow_dict = nx.maximum_flow(graph, source, sink)

    for u, v, capacity in graph.edges(data="capacity"):
        assert 0 <= flow_dict[u][v] <= capacity


@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_networkx_maximum_flow_skew_symmetry(graph, source_sink):
    source, sink = source_sink
    _, flow_dict = nx.maximum_flow(graph, source, sink)

    for u, v in graph.edges():
        assert flow_dict[u][v] == -flow_dict[v][u]


@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_networkx_maximum_flow_value_nonnegative(graph, source_sink):
    source, sink = source_sink
    flow_value, _ = nx.maximum_flow(graph, source, sink)
    assert flow_value >= 0


# This test is more complex and might require additional assumptions
# about the graph structure and capacity distribution. 
@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_networkx_maximum_flow_path_saturation(graph, source_sink):
    source, sink = source_sink
    flow_value, flow_dict = nx.maximum_flow(graph, source, sink)

    if flow_value < float('inf'):
        # Find a saturated path using a modified DFS
        def dfs(node, visited):
            if node == sink:
                return True
            visited.add(node)
            for neighbor in graph.successors(node):
                if neighbor not in visited and flow_dict[node][neighbor] == graph[node][neighbor]['capacity']:
                    if dfs(neighbor, visited):
                        return True
            return False
        
        assert dfs(source, set())

# End program