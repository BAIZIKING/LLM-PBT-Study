from hypothesis import given, strategies as st
from hypothesis.strategies import just, integers
import networkx as nx

@given(st.data())
def test_maximum_flow(data):
    # Generate a graph with a random (but reasonable) number of nodes.
    n = data.draw(st.integers(min_value=2, max_value=1000))
    nodes = range(n)

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    # Add edges with random capacities. 
    # An edge is added between each pair of nodes with a given probability.
    for node1 in nodes:
        for node2 in nodes:
            if node1 != node2 and data.draw(st.booleans()):
                G.add_edge(node1, node2, capacity=data.draw(st.floats(min_value=0.1, max_value=100.0)))
   
    # Randomly select source and target nodes.
    src, tgt = data.draw(st.lists(integers(min_value=0, max_value=n-1), min_size=2, max_size=2, unique=True))

    # Call the function to be tested.
    flow_value, flow_dict = nx.maximum_flow(G, src, tgt)
    
    # Check the properties.
    assert flow_value >= 0
    for node1, targets in flow_dict.items():
        for node2, flow in targets.items():
            assert 0 <= flow <= G[node1][node2]['capacity']
            if node1 != src and node1 != tgt:
                assert sum(flow_dict[node1].values()) - sum(flow_dict[node2][node1] for node2 in flow_dict if node1 in flow_dict[node2]) == 0