from hypothesis import given, strategies as st
import networkx as nx

@given(graph=st.graphs(), nbunch=st.sets(st.integers(min_value=0, max_value=100)), weight=st.sampled_from([None, "weight"]))
def test_networkx_degree_property(graph, nbunch, weight):
    if nbunch:
        nodes = list(nbunch)
        assert len(nx.degree(graph, nbunch, weight)) == len(nodes)
    else:
        assert len(nx.degree(graph, weight=weight)) == len(graph.nodes)

    for node, degree in nx.degree(graph, nbunch, weight):
        assert isinstance(degree, int)
        assert degree >= 0

    if weight is None:
        for node in graph.nodes:
            assert nx.degree(graph, node) == graph.degree(node)
    else:
        for node in graph.nodes:
            incident_edges = graph.edges(node, data=weight, default=1)
            expected_degree = sum(attr for _, _, attr in incident_edges)
            assert nx.degree(graph, node, weight) == expected_degree

    degree_view = nx.degree(graph, nbunch, weight)
    with pytest.raises(nx.NetworkXError):
        degree_view[0] = 10
# End program