from hypothesis import given, strategies as st, assume, example
import hypothesis_networkx as hnx
import networkx as nx
   
def test_maximum_flow(data):
    # Generate a random graph and ensure it has our desired properties
    G = data.draw(hnx.graphs(min_nodes=2))
    assume(nx.is_directed(G))
    assume(nx.is_connected(G))

    # Pick two distinct nodes from the graph
    nodes = list(G.nodes())
    _s, _t = data.draw(st.lists(st.sampled_from(nodes), min_size=2, max_size=2, unique=True))
    
    # Add a random capacity to the edges
    capacity_value = data.draw(st.integers(min_value=1, max_value=10))
    capacity_attr = data.draw(st.text())
    nx.set_edge_attributes(G, capacity_value, capacity_attr)
    
    flow_value, flow_dict = nx.maximum_flow(G, _s, _t, capacity=capacity_attr)
    
    # Test properties
    s_capacity = sum([G[_s][node][capacity_attr] for node in G[_s]])
    assert 0 <= flow_value <= s_capacity
    assert isinstance(flow_dict, dict)
    assert set(nodes).issubset(flow_dict.keys())