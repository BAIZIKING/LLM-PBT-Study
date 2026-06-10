from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs, node lists, and weight attributes.
@given(
    graph=st.one_of(
        st.graphs(graph_types=(nx.Graph, nx.DiGraph), min_nodes=0, max_nodes=10),
        st.just(nx.Graph()),
        st.just(nx.DiGraph())
    ),
    nbunch=st.one_of(
        st.lists(st.integers(), min_size=0, max_size=5),
        st.just(None)
    ),
    weight=st.one_of(st.none(), st.text())
)
def test_networkx_degree(graph, nbunch, weight):
    if nbunch is None:
        result = nx.degree(graph, weight=weight)
        assert isinstance(result, dict)
        for node, degree in result.items():
            assert isinstance(node, int)
            assert isinstance(degree, int)
    elif isinstance(nbunch, list):
        result = nx.degree(graph, nbunch, weight=weight)
        assert isinstance(result, dict)
        for node in nbunch:
            assert node in result
            assert isinstance(result[node], int)
    else:
        result = nx.degree(graph, nbunch, weight=weight)
        assert isinstance(result, int)

# End program