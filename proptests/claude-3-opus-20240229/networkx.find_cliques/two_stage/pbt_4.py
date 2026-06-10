from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_cliques_are_subgraphs(data):
    n = data.draw(st.integers(min_value=1, max_value=10))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    for clique in nx.find_cliques(G):
        assert nx.is_clique(G.subgraph(clique))

@given(st.data())
def test_cliques_are_maximal(data):
    n = data.draw(st.integers(min_value=1, max_value=10))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    for clique in nx.find_cliques(G):
        assert all(not set(clique) < set(c) for c in nx.find_cliques(G))

@given(st.data())
def test_cliques_contain_nodes(data):
    n = data.draw(st.integers(min_value=1, max_value=10))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    nodes = data.draw(st.lists(st.sampled_from(list(G.nodes())), min_size=1, max_size=n))
    if nx.is_clique(G.subgraph(nodes)):
        for clique in nx.find_cliques(G, nodes):
            assert set(nodes) <= set(clique)
    else:
        try:
            next(nx.find_cliques(G, nodes))
            assert False
        except ValueError:
            pass

@given(st.data())
def test_all_nodes_in_cliques(data):
    n = data.draw(st.integers(min_value=1, max_value=10))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    assert set(G.nodes()) == set.union(*(set(c) for c in nx.find_cliques(G)))

@given(st.integers(min_value=1, max_value=20))
def test_clique_number_upper_bound(n):
    G = nx.complete_graph(n)
    assert sum(1 for _ in nx.find_cliques(G)) <= 3 ** (n / 3)
# End program