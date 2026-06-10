from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate random graphs with varying number of nodes and edges
# - Optionally specify a subset of nodes that must be included in the cliques
# - Check that find_cliques returns an iterator
# - Check that each clique is a list of nodes 
# - Check that each clique forms a complete subgraph
# - Check that each clique is maximal (not a subset of any other clique)
# - Check that all returned cliques contain the required nodes (if provided)
# - Check that a ValueError is raised if required nodes don't form a clique

@given(st.data())
def test_find_cliques(data):
    # Generate a random graph
    n_nodes = data.draw(st.integers(min_value=0, max_value=10))
    n_edges = data.draw(st.integers(min_value=0, max_value=n_nodes*(n_nodes-1)//2))
    G = nx.gnm_random_graph(n_nodes, n_edges)
    
    # Optionally generate a subset of nodes to include
    req_nodes = data.draw(st.none() | st.lists(st.sampled_from(list(G.nodes)), 
                                               min_size=0, max_size=n_nodes))
    
    # Find cliques
    cliques = nx.find_cliques(G, nodes=req_nodes)
    
    # Check return type
    assert isinstance(cliques, types.GeneratorType)
    
    # Check clique properties
    for clique in cliques:
        assert isinstance(clique, list)
        assert len(set(clique)) == len(clique)  # no duplicates
        assert nx.is_clique(G, clique)  # forms a complete subgraph
        assert not any(set(clique) < set(c) for c in nx.find_cliques(G)) # maximal
        if req_nodes:
            assert set(req_nodes) <= set(clique)
            
    # Check required nodes
    if req_nodes and not nx.is_clique(G, req_nodes):
        with pytest.raises(ValueError):
            list(nx.find_cliques(G, nodes=req_nodes))
            
# End program            