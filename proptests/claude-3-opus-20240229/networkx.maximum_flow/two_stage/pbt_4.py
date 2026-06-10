from hypothesis import given, strategies as st
import networkx as nx

@given(
    st.graphs(
        nodes=st.integers(min_value=2, max_value=100),
        edges=st.integers(min_value=1, max_value=1000),
        directed=True,
    ),
    st.data(),
)
def test_flow_value_non_negative_and_bounded(graph, data):
    source = data.draw(st.sampled_from(list(graph.nodes)))
    sink = data.draw(st.sampled_from([n for n in graph.nodes if n != source]))
    
    # Assign random capacities to edges
    for u, v in graph.edges:
        graph[u][v]["capacity"] = data.draw(st.floats(min_value=0, max_value=1000))
    
    flow_value, _ = nx.maximum_flow(graph, source, sink)
    assert 0 <= flow_value <= sum(graph[source][v]["capacity"] for v in graph[source])

@given(
    st.graphs(
        nodes=st.integers(min_value=2, max_value=100),
        edges=st.integers(min_value=1, max_value=1000),
        directed=True,
    ),
    st.data(),
)
def test_flow_dict_respects_capacities(graph, data):
    source = data.draw(st.sampled_from(list(graph.nodes)))
    sink = data.draw(st.sampled_from([n for n in graph.nodes if n != source]))
    
    # Assign random capacities to edges
    for u, v in graph.edges:
        graph[u][v]["capacity"] = data.draw(st.floats(min_value=0, max_value=1000))
    
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for u, v in graph.edges:
        assert 0 <= flow_dict[u][v] <= graph[u][v]["capacity"]

@given(
    st.graphs(
        nodes=st.integers(min_value=2, max_value=100),
        edges=st.integers(min_value=1, max_value=1000),
        directed=True,
    ),
    st.data(),
)
def test_flow_conservation(graph, data):
    source = data.draw(st.sampled_from(list(graph.nodes)))
    sink = data.draw(st.sampled_from([n for n in graph.nodes if n != source]))
    
    # Assign random capacities to edges
    for u, v in graph.edges:
        graph[u][v]["capacity"] = data.draw(st.floats(min_value=0, max_value=1000))
    
    _, flow_dict = nx.maximum_flow(graph, source, sink)
    for node in graph.nodes:
        if node != source and node != sink:
            assert sum(flow_dict[u][node] for u in graph.predecessors(node)) == sum(
                flow_dict[node][v] for v in graph.successors(node)
            )

@given(
    st.graphs(
        nodes=st.integers(min_value=2, max_value=100),
        edges=st.integers(min_value=1, max_value=1000),
        directed=True,
    ),
    st.data(),
)
def test_increased_capacity_increases_flow(graph, data):
    source = data.draw(st.sampled_from(list(graph.nodes)))
    sink = data.draw(st.sampled_from([n for n in graph.nodes if n != source]))
    
    # Assign random capacities to edges
    for u, v in graph.edges:
        graph[u][v]["capacity"] = data.draw(st.floats(min_value=0, max_value=1000))
    
    flow_value1, _ = nx.maximum_flow(graph, source, sink)
    
    # Increase the capacity of a random edge
    u, v = data.draw(st.sampled_from(list(graph.edges)))
    graph[u][v]["capacity"] += data.draw(st.floats(min_value=1, max_value=1000))
    
    flow_value2, _ = nx.maximum_flow(graph, source, sink)
    assert flow_value2 >= flow_value1

@given(
    st.graphs(
        nodes=st.integers(min_value=2, max_value=100),
        edges=st.integers(min_value=0, max_value=0),
        directed=True,
    ),
    st.data(),
)
def test_disconnected_graph_zero_flow(graph, data):
    source = data.draw(st.sampled_from(list(graph.nodes)))
    sink = data.draw(st.sampled_from([n for n in graph.nodes if n != source]))
    
    flow_value, flow_dict = nx.maximum_flow(graph, source, sink)
    assert flow_value == 0
    assert all(flow == 0 for _, flows in flow_dict.items() for _, flow in flows.items())
# End program