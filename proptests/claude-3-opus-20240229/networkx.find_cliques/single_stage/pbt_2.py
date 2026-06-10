from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate random undirected graphs using hypothesis' graph strategy
# - Optionally generate a list of nodes to check for cliques containing those nodes
# - Check that find_cliques returns an iterator
# - Check that each returned clique is a list of nodes 
# - Check that each clique forms a complete subgraph
# - Check that all returned cliques are maximal (not a subset of any other clique)
# - If nodes parameter is provided, check that all returned cliques contain those nodes
# - Check that a ValueError is raised if nodes is provided but does not form a clique itself
@given(st.data())
def test_find_cliques(data):
    G = data.draw(st.graphs(directed=False))
    nodes = data.draw(st.none() | st.lists(st.sampled_from(list(G.nodes)), unique=True, min_size=1))
    
    cliques = nx.find_cliques(G, nodes)
    assert isinstance(cliques, types.GeneratorType)

    for clique in cliques:
        assert isinstance(clique, list)
        assert len(clique) == len(set(clique))
        assert nx.is_clique(G, clique)
        assert not any(set(clique) < set(c) for c in nx.find_cliques(G))
        if nodes is not None:
            assert set(nodes) <= set(clique)
            
    if nodes is not None and not nx.is_clique(G, nodes):
        with pytest.raises(ValueError):
            list(nx.find_cliques(G, nodes))