from hypothesis import given, strategies as st
import networkx


def _draw_graph(data, min_nodes=0, max_nodes=8):
    n = data.draw(st.integers(min_value=min_nodes, max_value=max_nodes), label="n")
    G = networkx.Graph()
    G.add_nodes_from(range(n))

    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                max_size=len(possible_edges),
            ),
            label="edges",
        )
        G.add_edges_from(edges)

    return G


def _is_clique(G, nodes):
    if len(nodes) != len(set(nodes)):
        return False
    if any(node not in G for node in nodes):
        return False

    nodes = list(nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if not G.has_edge(nodes[i], nodes[j]):
                return False
    return True


def _is_maximal_clique(G, nodes):
    if not _is_clique(G, nodes):
        return False

    node_set = set(nodes)
    for candidate in G:
        if candidate not in node_set:
            if all(G.has_edge(candidate, node) for node in node_set):
                return False
    return True


def _brute_force_maximal_cliques(G):
    graph_nodes = list(G.nodes)

    if not graph_nodes:
        return set()

    maximal_cliques = set()
    for mask in range(1, 1 << len(graph_nodes)):
        subset = [
            graph_nodes[index]
            for index in range(len(graph_nodes))
            if mask & (1 << index)
        ]

        if _is_maximal_clique(G, subset):
            maximal_cliques.add(frozenset(subset))

    return maximal_cliques


def _all_clique_subsets(G):
    graph_nodes = list(G.nodes)
    cliques = [[]]

    for mask in range(1, 1 << len(graph_nodes)):
        subset = [
            graph_nodes[index]
            for index in range(len(graph_nodes))
            if mask & (1 << index)
        ]
        if _is_clique(G, subset):
            cliques.append(subset)

    return cliques


@given(st.data())
def test_networkx_find_cliques_outputs_lists_of_distinct_graph_nodes(data):
    G = _draw_graph(data)

    for clique in networkx.find_cliques(G):
        assert isinstance(clique, list)
        assert len(clique) == len(set(clique))
        assert all(node in G for node in clique)


@given(st.data())
def test_networkx_find_cliques_outputs_complete_subgraphs(data):
    G = _draw_graph(data)

    for clique in networkx.find_cliques(G):
        assert _is_clique(G, clique)


@given(st.data())
def test_networkx_find_cliques_outputs_maximal_cliques(data):
    G = _draw_graph(data)

    for clique in networkx.find_cliques(G):
        assert _is_maximal_clique(G, clique)


@given(st.data())
def test_networkx_find_cliques_outputs_each_maximal_clique_exactly_once(data):
    G = _draw_graph(data)

    actual = [frozenset(clique) for clique in networkx.find_cliques(G)]

    assert len(actual) == len(set(actual))
    assert set(actual) == _brute_force_maximal_cliques(G)


@given(st.data())
def test_networkx_find_cliques_nodes_argument_filters_or_raises(data):
    G = _draw_graph(data)

    valid_node_sets = _all_clique_subsets(G)
    selected_nodes = data.draw(st.sampled_from(valid_node_sets), label="valid_nodes")

    actual = list(networkx.find_cliques(G, nodes=selected_nodes))
    selected_node_set = set(selected_nodes)

    assert all(selected_node_set.issubset(set(clique)) for clique in actual)

    expected = {
        clique
        for clique in _brute_force_maximal_cliques(G)
        if selected_node_set.issubset(clique)
    }

    assert len(actual) == len({frozenset(clique) for clique in actual})
    assert {frozenset(clique) for clique in actual} == expected

    invalid_graph = networkx.Graph()
    invalid_n = data.draw(st.integers(min_value=2, max_value=8), label="invalid_n")
    invalid_graph.add_nodes_from(range(invalid_n))

    possible_edges = [
        (i, j)
        for i in range(invalid_n)
        for j in range(i + 1, invalid_n)
    ]
    missing_edge = data.draw(st.sampled_from(possible_edges), label="missing_edge")
    allowed_edges = [edge for edge in possible_edges if edge != missing_edge]

    if allowed_edges:
        invalid_edges = data.draw(
            st.lists(
                st.sampled_from(allowed_edges),
                unique=True,
                max_size=len(allowed_edges),
            ),
            label="invalid_edges",
        )
        invalid_graph.add_edges_from(invalid_edges)

    try:
        list(networkx.find_cliques(invalid_graph, nodes=list(missing_edge)))
    except ValueError:
        pass
    else:
        assert False


# End program