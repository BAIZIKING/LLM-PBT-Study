from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate a random directed graph with random capacities.
# Check several properties:
# 1) Flow value returned is non-negative 
# 2) Flow along each edge does not exceed capacity
# 3) For each node, total flow in equals total flow out (except source and sink)
# 4) Residual network follows conventions 
# 5) Raises exceptions for unsupported graph types and infinite capacity paths
@given(
    num_nodes=st.integers(min_value=2, max_value=100),
    edge_prob=st.floats(min_value=0.1, max_value=1.0), 
    capacities=st.floats(min_value=0.0, max_value=1000.0)
)
def test_maximum_flow(num_nodes, edge_prob, capacities):
    # Generate random graph
    G = nx.gnp_random_graph(num_nodes, edge_prob, directed=True) 
    
    # Add random capacities
    for u,v in G.edges:
        G[u][v]['capacity'] = capacities
    
    # Check for valid source and sink
    source = None
    sink = None
    for n in G.nodes:
        if G.out_degree(n) >= 1 and G.in_degree(n) == 0:
            source = n
        if G.in_degree(n) >= 1 and G.out_degree(n) == 0:    
            sink = n
    assert source is not None and sink is not None, "Valid source and sink not found"
    
    if G.has_edge(source, sink):
        G.remove_edge(source, sink)
        
    # Compute max flow    
    try:
        flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    except nx.NetworkXUnbounded:
        # Check exception for infinite capacity
        assert any(G[u][v]['capacity'] == float('inf') for u,v in G.edges)
    except nx.NetworkXError:  
        # Check exception for unsupported graph type
        assert type(G) in [nx.MultiGraph, nx.MultiDiGraph]
    else:
        R = nx.DiGraph(flow_dict)
        # Check flow is non-negative
        assert flow_value >= 0
        # Check flow is within capacity constraints
        for u,v in G.edges:
            assert R[u][v]['flow'] <= G[u][v]['capacity']
        # Check flow conservation
        for n in G.nodes:
            if n not in (source, sink):  
                assert sum(R[n][v]['flow'] for v in R.successors(n)) == \
                       sum(R[u][n]['flow'] for u in R.predecessors(n))
        # Check residual network conventions
        assert all((u,v) in R.edges for u,v in G.edges if u != v)
        assert all(R[u][v]['flow'] == -R[v][u]['flow'] for u,v in R.edges)
        assert all(
            R[u][v]['capacity'] == G[u][v]['capacity'] if G.has_edge(u,v) else 0 
            for u,v in R.edges
        )
        assert 'inf' in R.graph
        assert 'flow_value' in R.graph
# End program