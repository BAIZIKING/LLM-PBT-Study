from hypothesis import given, strategies as st
import networkx


def _draw_small_dag(data):
    n = data.draw(st.integers(min_value=1, max_value=12), label="n")
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = data.draw(
        st.lists(
            st.sampled_from(possible_edges),
            unique=True,
            max_size=min(len(possible_edges), 40),
        ),
        label="edges",
    )

    G = networkx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    return G


def _common_ancestors(G, node1, node2):
    ancestors1 = networkx.ancestors(G, node1) | {node1}
    ancestors2 = networkx.ancestors(G, node2) | {node2}
    return ancestors1 & ancestors2


@given(st.data())
def test_networkx_lowest_common_ancestor_returns_graph_node_or_default(data):
    G = _draw_small_dag(data)
    node1 = data.draw(st.sampled_from(list(G.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(G.nodes)), label="node2")
    default = object()

    result = networkx.lowest_common_ancestor(G, node1, node2, default=default)

    assert result is default or result in G


@given(st.data())
def test_networkx_lowest_common_ancestor_result_is_common_ancestor(data):
    G = _draw_small_dag(data)
    node1 = data.draw(st.sampled_from(list(G.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(G.nodes)), label="node2")
    default = object()

    result = networkx.lowest_common_ancestor(G, node1, node2, default=default)

    if result is not default:
        assert networkx.has_path(G, result, node1)
        assert networkx.has_path(G, result, node2)


@given(st.data())
def test_networkx_lowest_common_ancestor_returns_default_iff_no_common_ancestor(data):
    G = _draw_small_dag(data)
    node1 = data.draw(st.sampled_from(list(G.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(G.nodes)), label="node2")
    default = object()

    result = networkx.lowest_common_ancestor(G, node1, node2, default=default)
    common = _common_ancestors(G, node1, node2)

    assert (result is default) == (len(common) == 0)


@given(st.data())
def test_networkx_lowest_common_ancestor_result_is_lowest(data):
    G = _draw_small_dag(data)
    node1 = data.draw(st.sampled_from(list(G.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(G.nodes)), label="node2")
    default = object()

    result = networkx.lowest_common_ancestor(G, node1, node2, default=default)

    if result is not default:
        common = _common_ancestors(G, node1, node2)
        for other in common:
            if other != result:
                assert not networkx.has_path(G, result, other)


@given(st.data())
def test_networkx_lowest_common_ancestor_is_symmetric(data):
    G = _draw_small_dag(data)
    node1 = data.draw(st.sampled_from(list(G.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(G.nodes)), label="node2")
    default = object()

    result1 = networkx.lowest_common_ancestor(G, node1, node2, default=default)
    result2 = networkx.lowest_common_ancestor(G, node2, node1, default=default)

    assert result1 == result2


# End program