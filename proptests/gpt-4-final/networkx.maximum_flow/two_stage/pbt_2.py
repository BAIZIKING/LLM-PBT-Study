from hypothesis import given, strategies as st
import networkx as nx
import math

def create_graph(edges_with_capacity):
    G = nx.DiGraph()
    for edge in edges_with_capacity:
        G.add_edge(edge[0], edge[1], capacity=edge[2])
    return G

@given(st.lists(st.tuples(st.text(min_size=1, max_size=1), st.text(min_size=1, max_size=1), st.integers(min_value=0, max_value=10)), min_size=1, max_size=5))
def test_networkx_maximum_flow_property(edges_with_capacity):
    G = create_graph(edges_with_capacity)
    source = edges_with_capacity[0][0]
    sink = edges_with_capacity[0][1]
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)

    # Property 1: flow_value is non-negative integer or float
    assert flow_value >= 0
    assert isinstance(flow_value, (int, float))

    # Property 2: flow_dict is a valid Python dictionary
    assert isinstance(flow_dict, dict)
    
    total_capacity = sum(edge[2] for edge in edges_with_capacity if edge[0] == source)

    # Property 4: The max flow is less than or equal to the sum of the total outgoing edges capacities from source.
    assert flow_value <= total_capacity

    # Property 3 and 5: flow_dict property checks
    for u, v in flow_dict.items():
        for w, flow in v.items():
            # Property 3: flow is negative of the reverse flow
            if w in flow_dict:
                assert flow == -flow_dict[w].get(u, 0)

            # Property 5: Flow doesn't exceed capacity
            assert math.isclose(flow, 0) or (0 <= flow <= G[u][w]['capacity'])