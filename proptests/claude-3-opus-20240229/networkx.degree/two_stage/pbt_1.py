from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_degree_view_is_dictionary(data):
    graph = nx.Graph(data.draw(st.dictionaries(keys=st.integers(), values=st.lists(st.integers()))))
    degree_view = nx.degree(graph)
    assert isinstance(degree_view, dict)
    assert all(isinstance(node, int) for node in degree_view.keys())
    assert all(isinstance(degree, int) for degree in degree_view.values())

@given(st.data())
def test_degree_view_includes_all_nodes_when_nbunch_is_none(data):
    graph = nx.Graph(data.draw(st.dictionaries(keys=st.integers(), values=st.lists(st.integers()))))
    degree_view = nx.degree(graph)
    assert set(degree_view.keys()) == set(graph.nodes())

@given(st.data())
def test_degree_view_single_node(data):
    graph = nx.Graph(data.draw(st.dictionaries(keys=st.integers(), values=st.lists(st.integers()))))
    node = data.draw(st.sampled_from(list(graph.nodes())))
    degree_view = nx.degree(graph, nbunch=node)
    assert len(degree_view) == 1
    assert node in degree_view

@given(st.data())
def test_degree_view_nbunch_of_nodes(data):
    graph = nx.Graph(data.draw(st.dictionaries(keys=st.integers(), values=st.lists(st.integers()))))
    nbunch = data.draw(st.lists(st.sampled_from(list(graph.nodes())), min_size=1, max_size=len(graph)))
    degree_view = nx.degree(graph, nbunch=nbunch)
    assert set(degree_view.keys()) == set(nbunch)

@given(st.data())
def test_degree_view_weighted(data):
    graph = nx.Graph(data.draw(st.dictionaries(keys=st.integers(), values=st.lists(st.tuples(st.integers(), st.floats())))))
    weight = data.draw(st.sampled_from([None, 'weight']))
    degree_view = nx.degree(graph, weight=weight)
    for node, degree in degree_view.items():
        if weight is None:
            assert degree == graph.degree(node)
        else:
            assert degree == sum(attr.get(weight, 1) for _, _, attr in graph.edges(node, data=True))
# End program