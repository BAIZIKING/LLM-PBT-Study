from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate a random directed graph with weighted edges.
# Pick two random nodes to use as source and sink.
# Optionally specify a capacity attribute name.
# Check that the maximum flow value is non-negative.
# Check that the flow on each edge does not exceed its capacity.
# Check that the net flow entering the source or leaving the sink
# equals the maximum flow value.
# Check that flow is conserved at all other nodes.
@given(
    G=st.builds(
        nx.DiGraph,
        edges=st.lists(
            st.tuples(st.integers(), st.integers(), st.dictionaries(st.sampled_from(['capacity', 'c', 'w']), st.floats(min_value=0, allow_infinity=True))), 
            min_size=1, unique=True,
        )
    ),
    s=st.integers(), 
    t=st.integers(),
    capacity_attr=st.sampled_from(['capacity', 'c', 'w', None]),
)
def test_maximum_flow(G, s, t, capacity_attr):
    # Discard invalid inputs
    assume(G.has_node(s) and G.has_node(t)) 
    assume(s != t)

    # Call maximum_flow
    flow_value, flow_dict = nx.maximum_flow(G, s, t, capacity=capacity_attr)

    # Check flow value is non-negative 
    assert flow_value >= 0

    inf = float('inf')

    # Check flow on edges does not exceed capacities
    for u, v, attr in G.edges(data=True):
        capacity = attr.get(capacity_attr, inf) 
        flow = flow_dict[u][v]
        assert flow >= 0
        assert flow <= capacity

    # Check conservation of flow at nodes
    for v in G:
        in_flow = sum(flow_dict[u][v] for u in G.predecessors(v))  
        out_flow = sum(flow_dict[v][w] for w in G.successors(v))
        if v == s:
            assert out_flow - in_flow == flow_value
        elif v == t:
            assert in_flow - out_flow == flow_value
        else:
            assert in_flow == out_flow
# End program