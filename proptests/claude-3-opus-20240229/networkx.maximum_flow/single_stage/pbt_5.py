from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# This test generates random directed graphs with weighted edges.
# The source and sink nodes are also randomly chosen.
# It checks several properties:
# 1. The returned flow value is non-negative 
# 2. The flow on each edge does not exceed its capacity
# 3. For each node, the total incoming flow equals the total outgoing flow (except source/sink)
# 4. Raises NetworkXUnbounded if the graph has a path of infinite capacity
@given(
    G=st.builds(nx.DiGraph),
    edge_weights=st.dictionaries(st.tuples(st.integers(), st.integers()), st.floats(min_value=0, allow_infinity=True)),
    source=st.integers(),  
    sink=st.integers()
)
def test_networkx_maximum_flow(G, edge_weights, source, sink):
    # Add edge capacities
    for (u, v), w in edge_weights.items():
        if G.has_edge(u, v):
            G[u][v]["capacity"] = w
            
    inf = float("inf")

    if source in G and sink in G and source != sink:
        if any(d.get("capacity", 0) == inf for u,v,d in G.edges(data=True)):
            with pytest.raises(nx.NetworkXUnbounded):
                flow_value, flow_dict = nx.maximum_flow(G, source, sink)
        else:
            flow_value, flow_dict = nx.maximum_flow(G, source, sink)

            # Test properties
            assert flow_value >= 0

            for u,v,d in G.edges(data=True):
                assert flow_dict[u][v] <= d.get("capacity", inf)

            for n in G.nodes():
                if n != source and n != sink:
                    assert sum(flow_dict[n][v] for v in G.successors(n)) == sum(
                        flow_dict[u][n] for u in G.predecessors(n)
                    )
# End program