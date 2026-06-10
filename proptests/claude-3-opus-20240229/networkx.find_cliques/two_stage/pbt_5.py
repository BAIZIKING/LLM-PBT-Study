from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cliques_output_format(data):
    n = data.draw(st.integers(min_value=1, max_value=20))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = nx.find_cliques(G)
    for clique in cliques:
        assert isinstance(clique, list)
        assert all(isinstance(node, int) for node in clique)

@given(st.data())
def test_find_cliques_maximality(data):
    n = data.draw(st.integers(min_value=1, max_value=20))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = list(nx.find_cliques(G))
    for i, clique1 in enumerate(cliques):
        for clique2 in cliques[i+1:]:
            assert not set(clique1).issubset(set(clique2))
            assert not set(clique2).issubset(set(clique1))

@given(st.data())
def test_find_cliques_with_nodes(data):
    n = data.draw(st.integers(min_value=1, max_value=20))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=n-1), min_size=1, max_size=n))
    if nx.is_clique(G, nodes):
        cliques = nx.find_cliques(G, nodes)
        for clique in cliques:
            assert set(nodes).issubset(set(clique))
    else:
        try:
            next(nx.find_cliques(G, nodes))
            assert False, "Expected ValueError for non-clique nodes"
        except ValueError:
            pass

@given(st.data())
def test_find_cliques_completeness(data):
    n = data.draw(st.integers(min_value=1, max_value=20))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = nx.find_cliques(G)
    for clique in cliques:
        assert nx.is_clique(G, clique)

@given(st.data())
def test_find_cliques_upper_bound(data):
    n = data.draw(st.integers(min_value=1, max_value=20))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = list(nx.find_cliques(G))
    assert len(cliques) <= min(3**(n/3), nx.combinations(n, n//3))
# End program