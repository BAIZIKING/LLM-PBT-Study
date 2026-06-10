from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cliques_output_type(data):
    n = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = nx.find_cliques(G)
    assert isinstance(cliques, types.GeneratorType)
    for clique in cliques:
        assert isinstance(clique, list)

@given(st.data())
def test_find_cliques_unique(data):
    n = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = list(nx.find_cliques(G))
    assert len(cliques) == len(set(tuple(sorted(c)) for c in cliques))

@given(st.data())
def test_find_cliques_with_nodes(data):
    n = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    nodes = data.draw(st.lists(st.sampled_from(list(G.nodes)), min_size=1, max_size=n))
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
def test_find_cliques_maximal(data):
    n = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = list(nx.find_cliques(G))
    for i, clique in enumerate(cliques):
        for j, other_clique in enumerate(cliques):
            if i != j:
                assert not set(clique).issubset(set(other_clique))

@given(st.data())
def test_find_cliques_nodes_in_graph(data):
    n = data.draw(st.integers(min_value=1, max_value=100))
    G = nx.gnp_random_graph(n, data.draw(st.floats(min_value=0, max_value=1)))
    cliques = nx.find_cliques(G)
    for clique in cliques:
        assert set(clique).issubset(set(G.nodes))
# End program