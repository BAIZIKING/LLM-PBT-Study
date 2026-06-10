from hypothesis import given, strategies as st
import networkx as nx

@given(graph=st.graphs(nodes=st.integers(min_value=0, max_value=100)))
def test_find_cliques_output_iterator_of_lists(graph):
    cliques = nx.find_cliques(graph)
    assert isinstance(cliques, Iterator)
    for clique in cliques:
        assert isinstance(clique, list)

@given(graph=st.graphs(nodes=st.integers(min_value=0, max_value=100)))
def test_find_cliques_unique_nodes(graph):
    cliques = nx.find_cliques(graph)
    for clique in cliques:
        assert len(clique) == len(set(clique))
        assert all(node in graph.nodes for node in clique)

@given(graph=st.graphs(nodes=st.integers(min_value=0, max_value=100)))
def test_find_cliques_complete_subgraph(graph):
    cliques = nx.find_cliques(graph)
    for clique in cliques:
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                assert graph.has_edge(clique[i], clique[j])

@given(graph=st.graphs(nodes=st.integers(min_value=0, max_value=100)), nodes=st.sets(elements=st.integers(min_value=0, max_value=100), max_size=10))
def test_find_cliques_with_nodes_argument(graph, nodes):
    nodes = list(nodes)
    if nx.is_clique(graph.subgraph(nodes)):
        cliques = nx.find_cliques(graph, nodes)
        for clique in cliques:
            assert all(node in clique for node in nodes)
    else:
        try:
            list(nx.find_cliques(graph, nodes))
            assert False, "Expected ValueError for non-clique nodes"
        except ValueError:
            pass

@given(graph=st.graphs(nodes=st.integers(min_value=0, max_value=100)), nodes=st.sets(elements=st.integers(min_value=0, max_value=100), max_size=10))
def test_find_cliques_raises_value_error_for_non_clique_nodes(graph, nodes):
    nodes = list(nodes)
    if not nx.is_clique(graph.subgraph(nodes)):
        try:
            list(nx.find_cliques(graph, nodes))
            assert False, "Expected ValueError for non-clique nodes"
        except ValueError:
            pass
# End program