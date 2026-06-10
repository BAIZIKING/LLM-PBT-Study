from hypothesis import given, strategies as st
import networkx


def _draw_unweighted_graph(data, min_nodes=0, max_nodes=12):
    node_count = data.draw(st.integers(min_value=min_nodes, max_value=max_nodes))
    nodes = list(range(node_count))
    possible_edges = [(u, v) for u in nodes for v in nodes if u <= v]

    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                max_size=min(40, len(possible_edges)),
                unique=True,
            )
        )
    else:
        edges = []

    graph = networkx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph, nodes


def _draw_weighted_graph(data, min_nodes=0, max_nodes=10):
    node_count = data.draw(st.integers(min_value=min_nodes, max_value=max_nodes))
    nodes = list(range(node_count))
    possible_edges = [(u, v) for u in nodes for v in nodes if u <= v]

    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                max_size=min(35, len(possible_edges)),
                unique=True,
            )
        )
    else:
        edges = []

    graph = networkx.Graph()
    graph.add_nodes_from(nodes)

    for u, v in edges:
        has_weight = data.draw(st.booleans())
        if has_weight:
            weight = data.draw(st.integers(min_value=-1000, max_value=1000))
            graph.add_edge(u, v, w=weight)
        else:
            graph.add_edge(u, v)

    return graph, nodes


def _manual_unweighted_degrees(graph):
    degrees = {node: 0 for node in graph.nodes}

    for u, v in graph.edges:
        if u == v:
            degrees[u] += 2
        else:
            degrees[u] += 1
            degrees[v] += 1

    return degrees


def _manual_weighted_degrees(graph, weight):
    degrees = {node: 0 for node in graph.nodes}

    for u, v, attrs in graph.edges(data=True):
        edge_weight = attrs.get(weight, 1)
        if u == v:
            degrees[u] += 2 * edge_weight
        else:
            degrees[u] += edge_weight
            degrees[v] += edge_weight

    return degrees


@given(st.data())
def test_networkx_degree_all_nodes_when_nbunch_omitted(data):
    graph, nodes = _draw_unweighted_graph(data)

    result = dict(networkx.degree(graph))

    assert set(result) == set(nodes)


@given(st.data())
def test_networkx_degree_single_node_returns_single_numeric_degree(data):
    graph, nodes = _draw_unweighted_graph(data, min_nodes=1)
    node = data.draw(st.sampled_from(nodes))

    result = networkx.degree(graph, node)
    expected = _manual_unweighted_degrees(graph)[node]

    assert isinstance(result, int)
    assert result == expected


@given(st.data())
def test_networkx_degree_iterable_nbunch_only_returns_nodes_present_in_graph(data):
    graph, nodes = _draw_unweighted_graph(data)

    if nodes:
        present_nodes = data.draw(
            st.lists(
                st.sampled_from(nodes),
                max_size=len(nodes),
                unique=True,
            )
        )
    else:
        present_nodes = []

    absent_pool = list(range(-20, 0)) + list(range(len(nodes), len(nodes) + 20))
    absent_nodes = data.draw(
        st.lists(
            st.sampled_from(absent_pool),
            max_size=10,
            unique=True,
        )
    )

    nbunch = present_nodes + absent_nodes
    result = dict(networkx.degree(graph, nbunch))

    assert set(result) == set(present_nodes)
    assert all(node in graph for node in result)


@given(st.data())
def test_networkx_degree_unweighted_values_are_non_negative_integers_and_count_self_loops_twice(data):
    graph, _ = _draw_unweighted_graph(data)

    result = dict(networkx.degree(graph))
    expected = _manual_unweighted_degrees(graph)

    assert result == expected
    assert all(isinstance(degree, int) for degree in result.values())
    assert all(degree >= 0 for degree in result.values())


@given(st.data())
def test_networkx_degree_weighted_values_sum_incident_edge_attributes_and_count_self_loops_twice(data):
    graph, _ = _draw_weighted_graph(data)

    result = dict(networkx.degree(graph, weight="w"))
    expected = _manual_weighted_degrees(graph, "w")

    assert result == expected
# End program