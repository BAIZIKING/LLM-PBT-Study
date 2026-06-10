from hypothesis import given, strategies as st, assume
from hypothesis import settings
from hypothesis.errors import InvalidArgument
import networkx as nx

# We limit the size of the graph to prevent tests from running too long
settings(max_examples=50)


@given(st.dictionaries(keys=st.tuples(st.integers(min_value=0, max_value=10),
                                    st.integers(min_value=0, max_value=10)),
                       values=st.integers(min_value=0, max_value=100),
                       min_size=3, max_size=100),
       st.integers(min_value=0, max_value=10),
       st.integers(min_value=0, max_value=10))
def test_networkx_maximum_flow_properties(graph, s, t):
    # Create a DiGraph from the input dictionary
    G = nx.DiGraph()
    G.add_weighted_edges_from((u, v, w) for (u, v), w in graph.items())

    # Check if s and t are in the graph and s != t
    assume(s in G and t in G and s != t)

    try:
        flow_value, flow_dict = nx.maximum_flow(G, s, t)
    except InvalidArgument:
        return
    except nx.NetworkXUnbounded:
        return

    # Property 1: The function returns two items
    assert isinstance(flow_value, (int, float))
    assert isinstance(flow_dict, dict)

    # Property 2: The flow_value is never negative
    assert flow_value >= 0

    # Property 3: The sum of all values in the flow_dict should be equal to the flow_value
    assert sum(sum(flow_dict[node].values()) for node in flow_dict) == flow_value * 2

    # Property 4: The flow from node "_s" to another node can't exceed the capacity of that edge
    for u, neighbors in flow_dict.items():
        if u == s:
            for v, flow in neighbors.items():
                assert 0 <= flow <= G[u][v]['capacity']

# End program