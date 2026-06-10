from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cliques_invariability_of_input_graph(data):
    G = nx.generators.random_graphs.fast_gnp_random_graph(5, 0.5)
    G_original = G.copy()
    cliques = nx.algorithms.clique.find_cliques(G)
    assert nx.utils.is_isomorphic(G, G_original)

@given(st.data())
def test_find_cliques_type_of_results(data):
    G = nx.generators.random_graphs.fast_gnp_random_graph(5, 0.5)
    cliques = nx.algorithms.clique.find_cliques(G)
    assert isinstance(cliques, type(iter([])))  # output is an iterator
    for clique in cliques:
        assert isinstance(clique, list)  # clique is a list of nodes
        for node in clique:
            assert node in G.nodes()  # nodes come from the graph G

@given(st.data())
def test_find_cliques_completeness_of_clique(data):
    G = nx.generators.random_graphs.fast_gnp_random_graph(5, 0.5)
    cliques = nx.algorithms.clique.find_cliques(G)
    for clique in cliques:
        for i in range(len(clique)):
            for j in range(i+1, len(clique)):
                assert G.has_edge(clique[i], clique[j])

@given(st.data())
def test_find_cliques_maximality_of_clique(data):
    G = nx.generators.random_graphs.fast_gnp_random_graph(5, 0.5)
    cliques = nx.algorithms.clique.find_cliques(G)
    for clique in cliques:
        for node in G.nodes():
            if node in clique:
                continue
            all_connected = all(G.has_edge(node, clique_node) for clique_node in clique)
            assert not all_connected

@given(st.data())
def test_find_cliques_preservation_of_confining_nodes(data):
    G = nx.generators.random_graphs.fast_gnp_random_graph(5, 0.5)
    nodes = data.draw(st.lists(st.sampled_from(list(G.nodes())), min_size=1, max_size=3, unique=True))
    if nx.algorithms.clique.is_clique(G, nodes):  # nodes form a clique
        cliques = nx.algorithms.clique.find_cliques(G)
        for clique in cliques:
            assert set(nodes).issubset(clique)
# End program