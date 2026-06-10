from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs (directed/undirected, varying sizes/densities) 
#          and node sets (cliques/non-cliques) to test find_cliques behavior.
@given(st.data())
def test_networkx_find_cliques(data):
    graph_type = data.draw(st.sampled_from([nx.Graph, nx.DiGraph]))
    num_nodes = data.draw(st.integers(min_value=0, max_value=10))
    edge_probability = data.draw(st.floats(min_value=0.0, max_value=1.0))
    graph = nx.gnp_random_graph(num_nodes, edge_probability, directed=graph_type is nx.DiGraph)

    if data.draw(st.booleans()):
        # Generate a random subset of nodes
        node_set = data.draw(st.sets(st.integers(min_value=0, max_value=num_nodes - 1)))
        is_clique = all(graph.has_edge(u, v) for u in node_set for v in node_set if u != v)

        if not is_clique:
            with pytest.raises(ValueError):
                list(nx.find_cliques(graph, nodes=list(node_set)))
        else:
            cliques = list(nx.find_cliques(graph, nodes=list(node_set)))
            for clique in cliques:
                assert all(node in clique for node in node_set)  # Check if nodes are present
                assert nx.is_clique(graph.subgraph(clique))     # Check if subgraph is a clique
    else:
        cliques = list(nx.find_cliques(graph))
        for clique in cliques:
            assert nx.is_clique(graph.subgraph(clique))  # Check if subgraph is a clique

# End program