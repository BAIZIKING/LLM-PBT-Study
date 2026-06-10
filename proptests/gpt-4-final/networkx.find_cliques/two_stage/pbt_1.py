from hypothesis import given, strategies as st
import networkx as nx

# Tha maximal cliques should be unique
@given(st.integers(min_value=2, max_value=10))
def test_unique_maximal_cliques(nodes_count):
    G = nx.generators.random_graphs.fast_gnp_random_graph(nodes_count, 0.5)
    cliques = list(nx.algorithms.find_cliques(G))
    assert len(cliques) == len(set(tuple(sorted(c)) for c in cliques))

# Clique should include specific nodes
@given(st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=5, unique=True))
def test_cliques_include_specific_nodes(nodes):
     G = nx.generators.random_graphs.fast_gnp_random_graph(11, 0.5)
     cliques = list(nx.find_cliques(G, nodes))
     assert any(all(node in c for node in nodes) for c in cliques)

# The size of cliques
@given(st.integers(min_value=2, max_value=10))
def test_maximal_clique_size(nodes_count):
    G = nx.generators.random_graphs.fast_gnp_random_graph(nodes_count, 0.5)
    cliques = list(nx.algorithms.find_cliques(G))
    max_clique_size = max(len(c) for c in cliques)
    assert all(len(c) <= max_clique_size for c in cliques)

# The completeness of cliques
@given(st.integers(min_value=2, max_value=10))
def test_completeness_of_cliques(nodes_count):
    G = nx.generators.random_graphs.fast_gnp_random_graph(nodes_count, 0.5)
    cliques = list(nx.algorithms.find_cliques(G))
    for c in cliques:
        subgraph = G.subgraph(c)
        assert nx.algorithms.is_chordal(subgraph)

# Error handling
@given(st.lists(st.integers(min_value=0, max_value=5), min_size=2, max_size=3, unique=True))
def test_nodes_not_a_clique(nodes):
    G = nx.path_graph(6)
    try:
        list(nx.find_cliques(G, nodes))
        assert False  # should have raised ValueError
    except ValueError:
        assert True