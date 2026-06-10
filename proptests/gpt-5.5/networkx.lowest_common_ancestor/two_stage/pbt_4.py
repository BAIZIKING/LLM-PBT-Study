from hypothesis import given, strategies as st
import networkx


def _draw_dag(data, min_nodes=1, max_nodes=8):
    n = data.draw(st.integers(min_value=min_nodes, max_value=max_nodes))
    graph = networkx.DiGraph()
    graph.add_nodes_from(range(n))

    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                max_size=min(len(possible_edges), 16),
            )
        )
        graph.add_edges_from(edges)

    return graph, n


def _draw_two_component_dag(data, min_nodes=2, max_nodes=8):
    n = data.draw(st.integers(min_value=min_nodes, max_value=max_nodes))
    split = data.draw(st.integers(min_value=1, max_value=n - 1))

    graph = networkx.DiGraph()
    graph.add_nodes_from(range(n))

    possible_edges = [
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if (i < split and j < split) or (i >= split and j >= split)
    ]
    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                max_size=min(len(possible_edges), 16),
            )
        )
        graph.add_edges_from(edges)

    node1 = data.draw(st.integers(min_value=0, max_value=split - 1))
    node2 = data.draw(st.integers(min_value=split, max_value=n - 1))

    return graph, node1, node2


def _ancestors_including_self(graph, node):
    return set(networkx.ancestors(graph, node)) | {node}


@given(st.data())
def test_networkx_lowest_common_ancestor_result_is_common_ancestor(data):
    graph, n = _draw_dag(data)
    node1 = data.draw(st.integers(min_value=0, max_value=n - 1))
    node2 = data.draw(st.integers(min_value=0, max_value=n - 1))
    default = ("no-common-ancestor",)

    result = networkx.lowest_common_ancestor(graph, node1, node2, default=default)

    if result != default:
        assert result in graph
        assert result in _ancestors_including_self(graph, node1)
        assert result in _ancestors_including_self(graph, node2)


@given(st.data())
def test_networkx_lowest_common_ancestor_returns_default_when_no_common_ancestor(data):
    graph, node1, node2 = _draw_two_component_dag(data)
    default = ("no-common-ancestor",)

    result = networkx.lowest_common_ancestor(graph, node1, node2, default=default)

    assert result == default


@given(st.data())
def test_networkx_lowest_common_ancestor_has_no_lower_common_ancestor(data):
    graph, n = _draw_dag(data)
    node1 = data.draw(st.integers(min_value=0, max_value=n - 1))
    node2 = data.draw(st.integers(min_value=0, max_value=n - 1))
    default = ("no-common-ancestor",)

    result = networkx.lowest_common_ancestor(graph, node1, node2, default=default)

    if result != default:
        common_ancestors = (
            _ancestors_including_self(graph, node1)
            & _ancestors_including_self(graph, node2)
        )
        strict_descendants_of_result = set(networkx.descendants(graph, result))

        assert common_ancestors.isdisjoint(strict_descendants_of_result)


@given(st.data())
def test_networkx_lowest_common_ancestor_is_symmetric(data):
    graph, n = _draw_dag(data)
    node1 = data.draw(st.integers(min_value=0, max_value=n - 1))
    node2 = data.draw(st.integers(min_value=0, max_value=n - 1))
    default = ("no-common-ancestor",)

    result1 = networkx.lowest_common_ancestor(graph, node1, node2, default=default)
    result2 = networkx.lowest_common_ancestor(graph, node2, node1, default=default)

    assert result1 == result2


@given(st.data())
def test_networkx_lowest_common_ancestor_of_node_with_itself_is_itself(data):
    graph, n = _draw_dag(data)
    node = data.draw(st.integers(min_value=0, max_value=n - 1))
    default = ("no-common-ancestor",)

    result = networkx.lowest_common_ancestor(graph, node, node, default=default)

    assert result == node


# End program