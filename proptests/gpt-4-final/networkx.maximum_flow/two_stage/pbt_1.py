from hypothesis import given, strategies as st
from hypothesis.strategies import lists, dictionaries
import networkx as nx

@given(
    st.lists(st.tuples(st.text(min_size=1, max_size=5), st.text(min_size=1, max_size=5), st.integers(min_value=0, max_value=10)), min_size=3, max_value=20),
    st.text(min_size=1, max_size=5),
    st.text(min_size=1, max_size=5)
)
def test_maximum_flow_properties(edges, source, target):
    
    # For case when the source or target is not in the graph
    nodes = list({node for edge in edges for node in edge[:2]})
    if source not in nodes or target not in nodes:
        return
    
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges, weight="capacity")

    flow_value, flow_dict = nx.maximum_flow(G, s=source, t=target)
    
    # Property 1 and 2
    assert isinstance(flow_value, (int, float)) and flow_value >= 0
    
    # Property 3
    assert all(edge in flow_dict for edge in edges)
    
    # Property 4
    for edge in edges:
        u, v, cap = edge
        assert flow_dict[u][v] <= cap

# End program