from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for generating graphs and source/sink nodes
def graph_strategy(max_nodes=10, max_capacity=100):
    # Generate a directed graph with random capacities
    return st.graphs(
        st.integers(2, max_nodes), 
        st.tuples(st.integers(), st.integers(1, max_capacity)),
        directed=True
    )

def source_sink_strategy(graph):
    # Choose source and sink nodes from the graph
    nodes = list(graph.nodes)
    return st.tuples(st.sampled_from(nodes), st.sampled_from(nodes))

# Test 1: Flow value is non-negative
@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_non_negative_flow(graph, source_sink):
    source, sink = source_sink
    flow_value, _ = nx.maximum_flow(graph, source, sink)
    assert flow_value >= 0

# Test 2: Flow conservation
@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_flow_conservation(graph, source_sink):
    source, sink = source_sink
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for node in graph.nodes:
        if node not in (source, sink):
            inflow = sum(flow_dict[u][node] for u in graph.predecessors(node))
            outflow = sum(flow_dict[node][v] for v in graph.successors(node))
            assert inflow == outflow 

# Test 3: Capacity constraints
@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_capacity_constraints(graph, source_sink):
    source, sink = source_sink
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for u, v in graph.edges:
        flow = flow_dict[u][v]
        capacity = graph[u][v].get('capacity', float('inf'))
        assert 0 <= flow <= capacity

# Test 4: Anti-symmetry of flow values
@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_flow_antisymmetry(graph, source_sink):
    source, sink = source_sink
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for u, v in graph.edges:
        assert flow_dict[u][v] == -flow_dict[v][u]

# Test 5: Flow value upper bounded by minimum cut capacity
@given(graph=graph_strategy(), source_sink=source_sink_strategy(graph))
def test_flow_min_cut_bound(graph, source_sink):
    source, sink = source_sink
    flow_value, _ = nx.maximum_flow(graph, source, sink)
    min_cut_value = nx.minimum_cut_value(graph, source, sink)
    assert flow_value <= min_cut_value 
# End program