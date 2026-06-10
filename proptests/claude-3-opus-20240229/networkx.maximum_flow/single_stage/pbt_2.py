from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate a random directed graph with weighted edges. Pick two random nodes s and t.
# Compute the maximum flow from s to t. Check that the computed flow satisfies
# the properties of a valid maximum flow:
# - Capacity constraints: flow on each edge <= capacity of the edge 
# - Conservation of flow: for each node except s and t, flow in = flow out
# - Value of flow equals value returned by maximum_flow
@given(
    # Generate a random directed graph
    g=st.builds(
        nx.DiGraph, 
        # Nodes are labeled 0, 1, ..., n-1
        st.integers(min_value=2, max_value=100) # num nodes
    ).map(
        lambda g: nx.DiGraph(
            (u, v, {'capacity': w})
            for (u, v), w in zip(g.edges, st.integers(min_value=1, max_value=1000).example())
        )
    ),
    # Source and sink are distinct nodes
    s=st.integers(min_value=0), 
    t=st.integers(min_value=0)
)
def test_maximum_flow_properties(g, s, t):
    # Num nodes in graph
    n = g.number_of_nodes() 
    # Adjust s and t to be in range and distinct
    s, t = s % n, (t % n + 1) % n
    assumed(s != t)

    flow_value, flow_dict = nx.maximum_flow(g, s, t)

    # Check flow conservation
    for u in g.nodes:
        if u == s or u == t:
            continue
        assert sum(flow_dict[u][v] for v in g.neighbors(u)) == \
               sum(flow_dict[v][u] for v in g.predecessors(u))
    
    # Check capacity constraints
    for u, v, attr in g.edges(data=True):
        assert flow_dict[u][v] <= attr['capacity']

    # Check computed flow value equals returned value
    assert sum(flow_dict[s][v] for v in g.neighbors(s)) - \
           sum(flow_dict[v][s] for v in g.predecessors(s)) == flow_value
# End program        