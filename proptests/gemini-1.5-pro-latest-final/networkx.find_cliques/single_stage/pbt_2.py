from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates random graphs and optional node subsets, checks properties of cliques found
@given(st.data())
def test_networkx_find_cliques(data):
    num_nodes = data.draw(st.integers(min_value=2, max_value=50))
    edge_prob = data.draw(st.floats(min_value=0, max_value=1))
    graph_type = data.draw(st.sampled_from(["gnp", "barabasi"]))
    
    if graph_type == "gnp":
        G = nx.gnp_random_graph(num_nodes, edge_prob)
    else:
        G = nx.barabasi_albert_graph(num_nodes, 3)  # m=3 for BA model
    
    node_subset = data.draw(
        st.one_of(
            st.just(None), 
            st.sets(st.integers(min_value=0, max_value=num_nodes - 1), min_size=1)
        )
    )
    
    if node_subset is not None and not nx.is_clique(G, node_subset):
        with pytest.raises(ValueError):
            list(nx.find_cliques(G, nodes=node_subset))
        return  # Stop test if ValueError is correctly raised

    for clique in nx.find_cliques(G, nodes=node_subset):
        # Check clique definition
        assert nx.is_clique(G, clique)
        
        # Check maximality
        for node in G:
            if node not in clique:
                assert not all(G.has_edge(node, c) for c in clique)

        # Check containment (if applicable)
        if node_subset:
            assert all(n in clique for n in node_subset)

# End program