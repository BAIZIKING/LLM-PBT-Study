from hypothesis import given, strategies as st

# Summary: 
# Generate a random graph by:
# 1) Generating a random number of nodes
# 2) Generating a random graph type (e.g. complete graph, cycle graph, random k-regular)  
# 3) Optionally generating a random subset of nodes to pass to find_cliques
# Check the following properties:
# 1) find_cliques returns an iterator
# 2) Each clique returned is a list 
# 3) Each node in each clique is in the original graph
# 4) Each clique forms a complete subgraph
# 5) If nodes parameter is provided, every clique contains all nodes in nodes
# 6) If nodes is provided but is not a clique itself, a ValueError is raised

@given(st.data())
def test_find_cliques(data):
    # Generate random graph
    n_nodes = data.draw(st.integers(min_value=1, max_value=10)) 
    graph_type = data.draw(st.sampled_from([nx.complete_graph, nx.cycle_graph, nx.random_regular_graph]))
    G = graph_type(n_nodes) 
    
    # Optionally generate subset of nodes
    use_nodes = data.draw(st.booleans())
    if use_nodes:
        nodes = data.draw(st.lists(st.integers(min_value=0, max_value=n_nodes-1), min_size=1, max_size=n_nodes, unique=True))
    else:
        nodes = None
    
    # Run find_cliques
    cliques = nx.find_cliques(G, nodes)
    
    # Check return type is an iterator
    assert isinstance(cliques, collections.abc.Iterator)
    
    for clique in cliques:
        # Check each clique is a list
        assert isinstance(clique, list)
        
        # Check each node in clique is in original graph 
        assert all(node in G for node in clique)
        
        # Check clique forms a complete subgraph
        assert nx.is_clique(G, clique)
        
        if nodes is not None:
            # Check clique contains all nodes in nodes
            assert all(node in clique for node in nodes)
            
    if nodes is not None:
        # Check ValueError is raised if nodes is not a clique
        if not nx.is_clique(G, nodes):
            with pytest.raises(ValueError):
                list(nx.find_cliques(G, nodes))
                
# End program