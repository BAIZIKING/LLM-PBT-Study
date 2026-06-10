from hypothesis import given, strategies as st
import networkx as nx

@given(graph=st.graphs(max_nodes=100, max_edges=1000))
def test_degree_length(graph):
    degree_view = nx.degree(graph)
    assert len(degree_view) == len(graph)

@given(graph=st.graphs(max_nodes=100, max_edges=1000))
def test_degree_non_negative(graph):
    degree_view = nx.degree(graph)
    assert all(d >= 0 for _, d in degree_view)

@given(graph=st.graphs(max_nodes=100, max_edges=1000))
def test_degree_sum(graph):
    degree_view = nx.degree(graph)
    assert sum(d for _, d in degree_view) == 2 * len(graph.edges)

@given(graph=st.graphs(max_nodes=100, max_edges=1000), node=st.integers(min_value=0, max_value=99))
def test_degree_single_node(graph, node):
    if node in graph:
        degree_view = nx.degree(graph, [node])
        assert len(degree_view) == 1
        assert degree_view[node] == graph.degree(node)

@given(graph=st.graphs(max_nodes=100, max_edges=1000), missing_nodes=st.lists(st.integers(min_value=-100, max_value=-1), max_size=10))
def test_degree_missing_nodes(graph, missing_nodes):
    degree_view = nx.degree(graph, missing_nodes)
    assert all(degree_view.get(node, 0) == 0 for node in missing_nodes)
# End program