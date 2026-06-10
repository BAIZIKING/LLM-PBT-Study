from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates various graphs, node bunches, and weight options to test networkx.degree
@given(
    graph=st.one_of(
        st.builds(nx.gnp_random_graph, st.integers(min_value=0, max_value=100), st.floats(min_value=0, max_value=1)),
        st.builds(nx.barabasi_albert_graph, st.integers(min_value=2, max_value=100), st.integers(min_value=1, max_value=5)),
        st.just(nx.complete_graph(5)),
        st.just(nx.empty_graph(5))
    ),
    nbunch=st.one_of(
        st.none(),
        st.sampled_from(list(range(10))),  # Assuming max 10 nodes in generated graphs
        st.lists(st.integers(), min_size=0, max_size=5),
    ),
    weight=st.one_of(st.none(), st.text())
)
def test_networkx_degree(graph, nbunch, weight):
    try:
        degrees = nx.degree(graph, nbunch, weight)
        if nbunch is None or isinstance(nbunch, list):
            assert isinstance(degrees, nx.classes.degree_view.DegreeView)
            for node, degree_value in degrees:
                if weight is None:
                    assert degree_value == len(list(graph.neighbors(node)))
                else:
                    assert degree_value == sum(data[weight] for _, _, data in graph.edges(node, data=True))
        else:
            assert isinstance(degrees, dict)
            if weight is None:
                assert degrees == len(list(graph.neighbors(nbunch)))
            else:
                assert degrees == sum(data[weight] for _, _, data in graph.edges(nbunch, data=True))
    except TypeError:
        assert not isinstance(graph, nx.Graph)
    except nx.NetworkXError:
        assert any(node not in graph for node in nbunch)
# End program