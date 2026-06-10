from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse graphs, node bunches, and weight parameters
@given(
    graph=st.one_of(
        st.builds(nx.Graph, st.lists(st.integers(min_value=0, max_value=10)), st.lists(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))),
        st.builds(nx.DiGraph, st.lists(st.integers(min_value=0, max_value=10)), st.lists(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))),
        st.builds(nx.MultiGraph, st.lists(st.integers(min_value=0, max_value=10)), st.lists(st.tuples(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10)))),
    ),
    nbunch=st.one_of(
        st.none(),
        st.lists(st.integers()), 
        st.sampled_from(list(range(10)))  # Sample from specific nodes
    ),
    weight=st.one_of(st.none(), st.integers(), st.floats())
)
def test_networkx_degree(graph, nbunch, weight):
    degree_view = nx.degree(graph, nbunch, weight)
    assert isinstance(degree_view, dict)
    
    for node, degree in degree_view.items():
        if node not in graph:
            assert degree == 0
        else:
            expected_degree = sum(data.get(weight, 1) for _, nbr, data in graph.edges(node, data=True))
            assert degree == expected_degree

# End program