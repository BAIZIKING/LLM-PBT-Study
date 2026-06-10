from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate random undirected graphs using hypothesis' graph strategy
# - Optionally generate a list of nodes to pass to find_cliques
# - Check that find_cliques returns an iterator
# - Check that each clique is a list of nodes
# - Check that each clique forms a complete subgraph
# - Check that each clique is maximal (not a subset of another clique) 
# - If nodes parameter is provided, check only cliques containing those nodes are returned
# - Check that a ValueError is raised if nodes is not a clique

@given(st.data())
def test_find_cliques(data):
    G = data.draw(nx.strategies.graphs(directed=False))
    nodes = data.draw(st.lists(st.sampled_from(list(G.nodes)), unique=True), label='nodes')
    use_nodes = data.draw(st.booleans(), label='use nodes')
    
    if use_nodes:
        try:
            cliques = list(nx.find_cliques(G, nodes))
        except ValueError:
            # Check that nodes is not a clique
            assert not nx.is_clique(G, nodes)
            return
    else:
        cliques = list(nx.find_cliques(G))
    
    # Check return type is an iterator
    assert iter(nx.find_cliques(G)) is iter(nx.find_cliques(G))
    
    for clique in cliques:
        # Check each clique is a list of nodes
        assert isinstance(clique, list)
        assert set(clique).issubset(G.nodes)
        
        # Check each clique forms a complete subgraph
        assert nx.is_clique(G, clique)
        
        # Check maximality 
        for node in set(G.nodes) - set(clique):
            assert not set(clique + [node]).issubset(G.nodes) or not nx.is_clique(G, clique + [node])
            
    if use_nodes:
        # Check only cliques containing nodes are returned 
        assert all(set(nodes).issubset(clique) for clique in cliques)
        
# End program