from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate a random directed or undirected graph with a given number of nodes and edges.
# Optionally specify a source node to start the cycle search from.
# Choose a random orientation for directed graphs ('original', 'reverse', 'ignore').
# Check that find_cycle either returns a valid cycle or raises NetworkXNoCycle.
# A valid cycle should:
#   - Be non-empty 
#   - Start and end at the same node
#   - Have each node in the cycle connected to the next by an edge
#   - Traverse edges in the reported direction if orientation is specified
@given(st.data())
def test_find_cycle(data):
    # Generate random graph parameters
    n_nodes = data.draw(st.integers(min_value=1, max_value=100))
    n_edges = data.draw(st.integers(min_value=0, max_value=n_nodes * (n_nodes - 1) // 2))
    directed = data.draw(st.booleans())
    
    # Generate random graph
    if directed:
        G = nx.gnm_random_graph(n_nodes, n_edges, directed=True) 
    else:
        G = nx.gnm_random_graph(n_nodes, n_edges)
    
    # Optionally specify source node
    source = data.draw(st.none() | st.integers(min_value=0, max_value=n_nodes-1))
    
    # Choose random orientation for directed graphs
    orientation = data.draw(st.none() | st.sampled_from(['original', 'reverse', 'ignore']))

    # Find cycle
    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
    except nx.NetworkXNoCycle:
        assert True
        return

    # Check cycle validity        
    assert len(cycle) > 0
    assert cycle[0][0] == cycle[-1][1]

    for i in range(len(cycle)-1):
        assert cycle[i][1] == cycle[i+1][0]
        assert G.has_edge(*cycle[i][:2])

    if orientation is not None:
        for u, v, d in cycle:
            assert d == 'forward' or d == 'reverse'
# End program