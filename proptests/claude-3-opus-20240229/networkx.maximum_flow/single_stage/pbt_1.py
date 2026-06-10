from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate random directed graphs with the following properties:
#   - Between 2 and 100 nodes
#   - Randomly add edges with capacity between nodes
# - Designate a random source and sink node
# - Compute the maximum flow
# - Check the following properties:
#   - flow_value is non-negative 
#   - flow_dict is a dict
#   - For each edge, the flow is less than or equal to the capacity
#   - For each node except the source and sink, the sum of flows in equals sum of flows out
#   - Sum of flows out of source equals flow_value
#   - Sum of flows into sink equals flow_value

@given(st.data())
def test_networkx_maximum_flow(data):
    
    # Generate random graph
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    G = nx.DiGraph()
    G.add_nodes_from(range(num_nodes))
    
    # Randomly add edges with random capacity
    for u, v in data.draw(st.sets(st.tuples(st.integers(0, num_nodes-1), st.integers(0, num_nodes-1)), min_size=1, max_size=num_nodes*num_nodes)):
        if u != v:
            G.add_edge(u, v, capacity=data.draw(st.floats(min_value=0, max_value=100)))

    # Skip test if graph is not connected
    if not nx.is_weakly_connected(G):
        data.mark_invalid()
    
    # Choose random source and sink
    source = data.draw(st.integers(0, num_nodes-1))
    sink = data.draw(st.integers(0, num_nodes-1))
    
    # Compute max flow
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    
    # Check properties
    assert flow_value >= 0
    assert isinstance(flow_dict, dict)
    
    for u, v, attr in G.edges(data=True):
        assert flow_dict[u][v] <= attr['capacity']
    
    for n in G.nodes:
        if n != source and n != sink:
            assert sum(flow_dict[u][n] for u in G.predecessors(n)) == sum(flow_dict[n][v] for v in G.successors(n))
    
    assert sum(flow_dict[source][v] for v in G.successors(source)) == flow_value
    assert sum(flow_dict[u][sink] for u in G.predecessors(sink)) == flow_value
# End program