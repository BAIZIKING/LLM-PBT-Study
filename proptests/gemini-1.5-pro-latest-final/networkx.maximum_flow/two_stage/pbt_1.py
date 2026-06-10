from hypothesis import given, strategies as st
import networkx as nx

# Define strategy for generating graphs with capacities
def graph_strategy(max_nodes=10, max_capacity=100):
    return st.graphs(
        st.integers(min_value=2, max_value=max_nodes),
        st.edges(label=st.integers(min_value=1, max_value=max_capacity)),
        min_edges=1,
    ).map(nx.DiGraph)

# Define strategy for source and sink nodes
def node_strategy(graph):
    return st.sampled_from(list(graph.nodes))

@given(graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_maximum_flow_non_negative(graph, source, sink):
    flow_value, _ = nx.maximum_flow(graph, source, sink)
    assert flow_value >= 0

@given(graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_maximum_flow_conservation(graph, source, sink):
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for node in graph.nodes:
        if node not in (source, sink):
            inflow = sum(flow_dict[u][node] for u in graph.predecessors(node))
            outflow = sum(flow_dict[node][v] for v in graph.successors(node))
            assert inflow == outflow

@given(graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_maximum_flow_capacity_constraints(graph, source, sink):
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for u, v, data in graph.edges(data=True):
        flow = flow_dict[u][v]
        capacity = data.get("capacity", float("inf"))
        assert flow <= capacity

@given(graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_maximum_flow_symmetry(graph, source, sink):
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for u, v in graph.edges():
        assert flow_dict[u][v] == -flow_dict[v][u]

@given(graph_strategy(), node_strategy(graph), node_strategy(graph))
def test_networkx_maximum_flow_path_saturation(graph, source, sink):
    flow_value, flow_dict = nx.maximum_flow(graph, source, sink)
    total_capacity = sum(data.get("capacity", float("inf")) for _, _, data in graph.edges(source, data=True))
    if flow_value < total_capacity:
        saturated_edges = [
            (u, v) for u, v, data in graph.edges(data=True) if flow_dict[u][v] == data.get("capacity", float("inf"))
        ]
        saturated_graph = nx.DiGraph(saturated_edges)
        assert nx.has_path(saturated_graph, source, sink)
# End program