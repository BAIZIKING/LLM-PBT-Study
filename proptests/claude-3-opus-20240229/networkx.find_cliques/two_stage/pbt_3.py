from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cliques_output_type(data):
    n_nodes = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n_nodes, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = nx.find_cliques(G)
    assert isinstance(cliques, types.GeneratorType)
    for clique in cliques:
        assert isinstance(clique, list)
        assert all(isinstance(node, int) for node in clique)

@given(st.data())
def test_find_cliques_with_nodes_argument(data):
    n_nodes = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n_nodes, data.draw(st.floats(min_value=0, max_value=1)))
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=n_nodes-1), min_size=1, max_size=n_nodes, unique=True))
    if nx.is_clique(G, nodes):
        cliques = list(nx.find_cliques(G, nodes))
        assert all(set(nodes).issubset(set(clique)) for clique in cliques)
    else:
        try:
            list(nx.find_cliques(G, nodes))
            assert False, "Expected ValueError for non-clique nodes"
        except ValueError:
            pass

@given(st.data())
def test_find_cliques_maximality(data):
    n_nodes = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n_nodes, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = list(nx.find_cliques(G))
    for i, clique1 in enumerate(cliques):
        for clique2 in cliques[i+1:]:
            assert not set(clique1).issubset(set(clique2))
            assert not set(clique2).issubset(set(clique1))

@given(st.data())
def test_find_cliques_node_coverage(data):
    n_nodes = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n_nodes, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = list(nx.find_cliques(G))
    assert set().union(*cliques).issubset(set(G.nodes))

@given(st.data())
def test_find_cliques_isomorphism_invariance(data):
    n_nodes = data.draw(st.integers(min_value=1, max_value=10))
    G1 = nx.gnp_random_graph(n_nodes, data.draw(st.floats(min_value=0, max_value=1)))
    G2 = nx.relabel_nodes(G1, {n: i for i, n in enumerate(G1.nodes)})
    cliques1 = [set(c) for c in nx.find_cliques(G1)]
    cliques2 = [set(c) for c in nx.find_cliques(G2)]
    assert cliques1 == cliques2
# End program