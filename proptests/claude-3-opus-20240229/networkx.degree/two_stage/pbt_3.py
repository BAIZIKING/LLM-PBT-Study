from hypothesis import given, strategies as st
import networkx as nx

@given(graph=st.builds(nx.Graph, st.lists(st.tuples(st.integers(), st.integers()))))
def test_degree_view_is_dictionary(graph):
    degree_view = nx.degree(graph)
    assert isinstance(degree_view, dict)
    assert set(degree_view.keys()) == set(graph.nodes())

@given(graph=st.builds(nx.Graph, st.lists(st.tuples(st.integers(), st.integers()))),
       nbunch=st.none())
def test_degree_view_includes_all_nodes(graph, nbunch):
    degree_view = nx.degree(graph, nbunch)
    assert set(degree_view.keys()) == set(graph.nodes())

@given(graph=st.builds(nx.Graph, st.lists(st.tuples(st.integers(), st.integers()))),
       node=st.integers())
def test_degree_view_single_node(graph, node):
    degree_view = nx.degree(graph, [node])
    assert len(degree_view) == 1
    assert node in degree_view

@given(graph=st.builds(nx.Graph, st.lists(st.tuples(st.integers(), st.integers()))),
       weight=st.none())
def test_degree_values_are_integers(graph, weight):
    degree_view = nx.degree(graph, weight=weight)
    assert all(isinstance(val, int) for val in degree_view.values())

@given(graph=st.builds(nx.Graph, st.lists(st.tuples(st.integers(), st.integers()))))
def test_degree_sum_equals_twice_num_edges(graph):
    degree_view = nx.degree(graph)
    assert sum(degree_view.values()) == 2 * graph.number_of_edges()
# End program