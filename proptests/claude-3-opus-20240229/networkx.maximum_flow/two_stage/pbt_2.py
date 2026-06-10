from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_flow_value_non_negative_and_bounded(data):
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    G = nx.DiGraph()
    nodes = range(num_nodes)
    G.add_nodes_from(nodes)
    for u, v in data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=1)):
        if u != v:
            G.add_edge(u, v, capacity=data.draw(st.floats(min_value=0, max_value=1000)))
    
    source = data.draw(st.sampled_from(nodes))
    sink = data.draw(st.sampled_from([n for n in nodes if n != source]))
    
    flow_value, _ = nx.maximum_flow(G, source, sink)
    assert flow_value >= 0
    assert flow_value <= sum(G[source][v]['capacity'] for v in G.neighbors(source))

@given(st.data())
def test_flow_dict_non_negative_and_bounded(data):
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    G = nx.DiGraph()
    nodes = range(num_nodes)
    G.add_nodes_from(nodes)
    for u, v in data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=1)):
        if u != v:
            G.add_edge(u, v, capacity=data.draw(st.floats(min_value=0, max_value=1000)))
    
    source = data.draw(st.sampled_from(nodes))
    sink = data.draw(st.sampled_from([n for n in nodes if n != source]))
    
    _, flow_dict = nx.maximum_flow(G, source, sink)
    for u, v in G.edges():
        assert flow_dict[u][v] >= 0
        assert flow_dict[u][v] <= G[u][v]['capacity']

@given(st.data())
def test_total_flow_entering_sink(data):
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    G = nx.DiGraph()
    nodes = range(num_nodes)
    G.add_nodes_from(nodes)
    for u, v in data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=1)):
        if u != v:
            G.add_edge(u, v, capacity=data.draw(st.floats(min_value=0, max_value=1000)))
    
    source = data.draw(st.sampled_from(nodes))
    sink = data.draw(st.sampled_from([n for n in nodes if n != source]))
    
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    assert sum(flow_dict[u][sink] for u in G.predecessors(sink)) == flow_value

@given(st.data())
def test_flow_conservation(data):
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    G = nx.DiGraph()
    nodes = range(num_nodes)
    G.add_nodes_from(nodes)
    for u, v in data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=1)):
        if u != v:
            G.add_edge(u, v, capacity=data.draw(st.floats(min_value=0, max_value=1000)))
    
    source = data.draw(st.sampled_from(nodes))
    sink = data.draw(st.sampled_from([n for n in nodes if n != source]))
    
    _, flow_dict = nx.maximum_flow(G, source, sink)
    for n in nodes:
        if n != source and n != sink:
            assert sum(flow_dict[u][n] for u in G.predecessors(n)) == sum(flow_dict[n][v] for v in G.successors(n))

@given(st.data())
def test_max_flow_min_cut(data):
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    G = nx.DiGraph()
    nodes = range(num_nodes)
    G.add_nodes_from(nodes)
    for u, v in data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), min_size=1)):
        if u != v:
            G.add_edge(u, v, capacity=data.draw(st.floats(min_value=0, max_value=1000)))
    
    source = data.draw(st.sampled_from(nodes))
    sink = data.draw(st.sampled_from([n for n in nodes if n != source]))
    
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    if flow_value == sum(G[source][v]['capacity'] for v in G.neighbors(source)):
        cut_value, (S, T) = nx.minimum_cut(G, source, sink)
        assert flow_value == cut_value
        assert source in S
        assert sink in T
# End program