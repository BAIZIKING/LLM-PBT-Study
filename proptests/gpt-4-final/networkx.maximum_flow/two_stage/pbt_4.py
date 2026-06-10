from hypothesis import given, strategies as st
import networkx as nx
import pytest

@given(st.dictionaries(keys=st.text(), 
       values=st.dictionaries(keys=st.text(), 
       values=st.fixed_dictionaries({'capacity': st.floats(min_value=1, max_value=100)}))),
       st.text(), st.text())
def test_networkx_maximum_flow_property(edges_dict, node_s, node_t):
    # Construct a DiGraph with the given edges dictionary
    G = nx.DiGraph(edges_dict)

    # Catch the exceptions raised by maximum_flow
    try:
        flow_value, flow_dict = nx.maximum_flow(G, node_s, node_t)
    except (nx.NetworkXError, nx.NetworkXUnbounded):
        pytest.skip("NetworkXError or NetworkXUnbounded was raised")
  
    # Check that flow_value is a number, and flow_dict is a dict
    assert isinstance(flow_value, (int, float))
    assert isinstance(flow_dict, dict)

    # Skip further testing if the graph doesn't contain the source and the target
    if node_s not in G.nodes or node_t not in G.nodes:
        pytest.skip("The source or the target is not in the graph")

    # Check flow conservation for all nodes except the source and sink
    for node in G.nodes:
        if node == node_s or node == node_t:
            continue
        inflow = sum(flow_dict[p][node] for p in G.predecessors(node))
        outflow = sum(flow_dict[node][s] for s in G.successors(node))
        assert inflow == outflow

    # Check that flow value of an edge does not exceed its capacity
    for u, v, capacity in G.edges.data('capacity'):
        assert flow_dict[u][v] <= capacity