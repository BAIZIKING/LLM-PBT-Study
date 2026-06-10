from hypothesis import given, strategies as st
import networkx


def _draw_dag(data, min_nodes=1, max_nodes=12, label_prefix=""):
    n = data.draw(
        st.integers(min_value=min_nodes, max_value=max_nodes),
        label=f"{label_prefix}n",
    )
    graph = networkx.DiGraph()
    graph.add_nodes_from(range(n))

    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                max_size=len(possible_edges),
            ),
            label=f"{label_prefix}edges",
        )
        graph.add_edges_from(edges)

    return graph


def _draw_dag_on_nodes(data, nodes, label_prefix=""):
    graph = networkx.DiGraph()
    graph.add_nodes_from(nodes)

    possible_edges = [(u, v) for u in nodes for v in nodes if u < v]
    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                max_size=len(possible_edges),
            ),
            label=f"{label_prefix}edges",
        )
        graph.add_edges_from(edges)

    return graph


def _is_ancestor_or_self(graph, ancestor, node):
    return ancestor == node or networkx.has_path(graph, ancestor, node)


def _common_ancestors_including_self(graph, node1, node2):
    return {
        node
        for node in graph.nodes
        if _is_ancestor_or_self(graph, node, node1)
        and _is_ancestor_or_self(graph, node, node2)
    }


@given(st.data())
def test_networkx_lowest_common_ancestor_is_symmetric(data):
    graph = _draw_dag(data)
    node1 = data.draw(st.sampled_from(list(graph.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(graph.nodes)), label="node2")
    default = "__DEFAULT__"

    result1 = networkx.lowest_common_ancestor(graph, node1, node2, default=default)
    result2 = networkx.lowest_common_ancestor(graph, node2, node1, default=default)

    assert result1 == result2


@given(st.data())
def test_networkx_lowest_common_ancestor_of_node_with_itself_is_that_node(data):
    graph = _draw_dag(data)
    node = data.draw(st.sampled_from(list(graph.nodes)), label="node")
    default = "__DEFAULT__"

    result = networkx.lowest_common_ancestor(graph, node, node, default=default)

    assert result == node


@given(st.data())
def test_networkx_lowest_common_ancestor_result_is_common_ancestor_when_not_default(data):
    graph = _draw_dag(data)
    node1 = data.draw(st.sampled_from(list(graph.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(graph.nodes)), label="node2")
    default = "__DEFAULT__"

    result = networkx.lowest_common_ancestor(graph, node1, node2, default=default)

    if result != default:
        assert result in graph
        assert _is_ancestor_or_self(graph, result, node1)
        assert _is_ancestor_or_self(graph, result, node2)


@given(st.data())
def test_networkx_lowest_common_ancestor_returns_default_when_no_common_ancestor(data):
    left_size = data.draw(st.integers(min_value=1, max_value=6), label="left_size")
    right_size = data.draw(st.integers(min_value=1, max_value=6), label="right_size")

    left_nodes = list(range(left_size))
    right_nodes = list(range(left_size, left_size + right_size))

    left_graph = _draw_dag_on_nodes(data, left_nodes, label_prefix="left_")
    right_graph = _draw_dag_on_nodes(data, right_nodes, label_prefix="right_")

    graph = networkx.compose(left_graph, right_graph)

    node1 = data.draw(st.sampled_from(left_nodes), label="node1")
    node2 = data.draw(st.sampled_from(right_nodes), label="node2")
    default = "__DEFAULT__"

    result = networkx.lowest_common_ancestor(graph, node1, node2, default=default)

    assert _common_ancestors_including_self(graph, node1, node2) == set()
    assert result == default


@given(st.data())
def test_networkx_lowest_common_ancestor_result_is_lowest_when_not_default(data):
    graph = _draw_dag(data)
    node1 = data.draw(st.sampled_from(list(graph.nodes)), label="node1")
    node2 = data.draw(st.sampled_from(list(graph.nodes)), label="node2")
    default = "__DEFAULT__"

    result = networkx.lowest_common_ancestor(graph, node1, node2, default=default)

    if result != default:
        common_ancestors = _common_ancestors_including_self(graph, node1, node2)
        for other in common_ancestors:
            assert other == result or not networkx.has_path(graph, result, other)


# End program