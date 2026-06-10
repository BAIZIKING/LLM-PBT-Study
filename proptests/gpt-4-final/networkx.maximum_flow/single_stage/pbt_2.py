from hypothesis import given, strategies as st
import networkx as nx
import numpy as np

# Constructs graphs with random capacities
def generate_random_graph(graph_size):
    G = nx.DiGraph()
    for node in range(1, graph_size + 1):
        next_node = np.random.randint(1, graph_size + 1)
        while next_node == node:
            next_node = np.random.randint(1, graph_size + 1) # Ensure no self-loops
        G.add_edge(node, next_node, capacity=np.random.uniform())
    return G

# Strategy: We generate random directed graphs with a moderate number of nodes/edges. The capacities of the edges are randomly assigned.
@given(st.data())
def test_maximum_flow(data):
    number_of_nodes = data.draw(st.integers(min_value=2, max_value=50), label="number_of_nodes")
    G = generate_random_graph(number_of_nodes)
    source = data.draw(st.integers(min_value=1, max_value=number_of_nodes), label="source")
    sink = data.draw(st.integers(min_value=1, max_value=number_of_nodes))
    while source == sink: # Ensure source & sink doesn't coincide
        sink = data.draw(st.integers(min_value=1, max_value=number_of_nodes))
    
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    
    assert isinstance(flow_value, (float, int)) 
    assert isinstance(flow_dict, dict)
    
    total_capacity = sum(edge[2]['capacity'] for edge in G.edges(data=True))
    assert round(flow_value, 6) <= round(total_capacity, 6) # Check 
    assert round(flow_value, 6) >= 0
# End program