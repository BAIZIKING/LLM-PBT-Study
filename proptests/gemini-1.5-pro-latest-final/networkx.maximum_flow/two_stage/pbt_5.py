from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for graph generation with reasonable size and capacity limitations
nodes = st.integers(min_value=2, max_value=100)  # Limit number of nodes
edges = st.tuples(st.integers(), st.integers(), st.integers(min_value=1, max_value=100))
graphs = st.builds(nx.DiGraph, st.tuples(nodes, edges))

@given(graphs, st.data())
def test_networkx_maximum_flow_non_negativity(graph, data):
    source = data.draw(st.sampled_from(graph.nodes))
    target = data.draw(st.sampled_from(graph.nodes))
    flow_value, _ = nx.maximum_flow(graph, source, target)
    assert flow_value >= 0

@given(graphs, st.data())
def test_networkx_maximum_flow_conservation(graph, data):
    source = data.draw(st.sampled_from(graph.nodes))
    target = data.draw(st.sampled_from(graph.nodes))
    _, flow_dict = nx.maximum_flow(graph, source, target)
    for node in graph.nodes:
        if node != source and node != target:
            inflow = sum(flow_dict[u][node] for u in graph.predecessors(node))
            outflow = sum(flow_dict[node][v] for v in graph.successors(node))
            assert inflow == outflow

@given(graphs, st.data())
def test_networkx_maximum_flow_capacity_constraints(graph, data):
    source = data.draw(st.sampled_from(graph.nodes))
    target = data.draw(st.sampled_from(graph.nodes))
    _, flow_dict = nx.maximum_flow(graph, source, target)
    for u, v in graph.edges:
        capacity = graph[u][v].get('capacity', float('inf'))
        assert 0 <= flow_dict[u][v] <= capacity

@given(graphs, st.data())
def test_networkx_maximum_flow_skew_symmetry(graph, data):
    source = data.draw(st.sampled_from(graph.nodes))
    target = data.draw(st.sampled_from(graph.nodes))
    _, flow_dict = nx.maximum_flow(graph, source, target)
    for u, v in graph.edges:
        assert flow_dict[u][v] == -flow_dict[v][u]

@given(graphs, st.data())
def test_networkx_maximum_flow_path_saturation(graph, data):
    source = data.draw(st.sampled_from(graph.nodes))
    target = data.draw(st.sampled_from(graph.nodes))
    _, flow_dict = nx.maximum_flow(graph, source, target)
    residual_graph = nx.algorithms.flow.utils.build_residual_network(graph, flow_dict)
    try:
        nx.algorithms.shortest_paths.generic.has_path(residual_graph, source, target)
        assert False, "Path with residual capacity exists, flow not maximum"
    except nx.NetworkXNoPath:
        pass  # Expected behavior for maximum flow
# End program