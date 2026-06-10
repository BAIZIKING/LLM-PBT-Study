from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate a random directed or undirected graph with a mix of acyclic and cyclic components.
# Parameters to vary include:
# - Number of nodes (small <= 10, medium <= 100, large <= 1000) 
# - Edge probability (sparse < 0.2, medium, dense > 0.6)
# - Directed vs undirected
# - Allowing self-loops and parallel edges
# 
# Check the following properties:
# - If no cycle exists, NetworkXNoCycle should be raised
# - If a cycle is returned, it should be a valid cycle in the graph 
# - Cycles should be found irrespective of source node
# - Orientation parameter should control edge directions in result
@given(st.data())
def test_find_cycle(data):
    # Generate random graph parameters
    n_nodes = data.draw(st.sampled_from([10, 100, 1000])) 
    edge_prob = data.draw(st.sampled_from([0.1, 0.4, 0.8]))
    directed = data.draw(st.booleans())
    allow_selfloops = data.draw(st.booleans())
    
    # Generate random graph
    if directed:
        G = nx.gnp_random_graph(n_nodes, edge_prob, directed=True)
        if allow_selfloops:
            G.add_edges_from([(n,n) for n in G.nodes() if data.draw(st.booleans())])
    else:
        G = nx.gnp_random_graph(n_nodes, edge_prob)
        
    # Test with different source nodes
    source_nodes = data.draw(st.lists(st.sampled_from(list(G.nodes())), min_size=1, max_size=3))
    for source in source_nodes:
        
        # Test with different orientation settings
        for orientation in [None, 'original', 'reverse', 'ignore']:
            try:
                cycle = nx.find_cycle(G, source, orientation)
                
                # Check cycle is valid
                assert len(cycle) == len(set(cycle)) # no duplicated edges
                assert all(G.has_edge(*e[:2]) for e in cycle)  # all edges exist
                
                if directed:
                    # Check orientation
                    if orientation == 'reverse':
                        assert all(e[-1] == 'reverse' for e in cycle)
                    elif orientation == 'original':
                        assert all(e[-1] == 'forward' for e in cycle)
                    elif orientation == 'ignore':
                        assert all(e[-1] in ['forward', 'reverse'] for e in cycle)
                        
            except nx.NetworkXNoCycle:
                # Check graph is acyclic 
                assert nx.is_directed_acyclic_graph(G)
# End program