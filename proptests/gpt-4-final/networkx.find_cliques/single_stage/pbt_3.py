from hypothesis import given, assume, strategies as st, settings
import networkx as nx

def find_maximal_cliques(G):
    return list(nx.find_cliques(G))

@settings(max_examples=50)
@given(G=st.builds(nx.gnp_random_graph, n=st.integers(min_value=0, max_value=20), p=st.floats(min_value=0, max_value=1)), 
       nodes=st.one_of(st.none(), st.lists(st.integers(min_value=0, max_value=19))))
def test_find_cliques(G, nodes):
    try:
        cliques = find_maximal_cliques(G)

        # Check that the function returns a list
        assert isinstance(cliques, list)
        
        if nodes is not None:
            # If nodes are provided, cliques should contain all these nodes
            for node in nodes:
                assert all(node in clique for clique in cliques)
                
        # Ensure cliques are maximal (not contained within another)
        for clique_1 in cliques:
            for clique_2 in cliques:
                if clique_1 != clique_2:
                    assert set(clique_1).issubset(clique_2) == False

    except ValueError:
        # if nodes is not a clique catch ValueError
        nodes_subgraph = G.subgraph(nodes)
        assert not nx.is_clique(nodes_subgraph)
# End program