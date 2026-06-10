from hypothesis import given, strategies as st
import networkx


def _draw_graph(data, max_nodes=8):
    n = data.draw(st.integers(min_value=0, max_value=max_nodes))
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = data.draw(st.lists(st.sampled_from(possible_edges), unique=True)) if possible_edges else []

    graph = networkx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(edges)
    return graph


@given(st.data())
def test_find_cliques_yields_only_graph_nodes_without_repetition(data):
    G = _draw_graph(data)

    for clique in networkx.find_cliques(G):
        assert len(clique) == len(set(clique))
        assert all(node in G for node in clique)


@given(st.data())
def test_find_cliques_yields_complete_subgraphs(data):
    G = _draw_graph(data)

    for clique in networkx.find_cliques(G):
        for i, u in enumerate(clique):
            for v in clique[i + 1:]:
                assert G.has_edge(u, v)


@given(st.data())
def test_find_cliques_yields_only_maximal_cliques(data):
    G = _draw_graph(data)

    for clique in networkx.find_cliques(G):
        clique_set = set(clique)

        for outside_node in set(G.nodes) - clique_set:
            assert any(
                not G.has_edge(outside_node, clique_node)
                for clique_node in clique_set
            )


@given(st.data())
def test_find_cliques_does_not_yield_duplicate_cliques(data):
    G = _draw_graph(data)

    normalized_cliques = [frozenset(clique) for clique in networkx.find_cliques(G)]

    assert len(normalized_cliques) == len(set(normalized_cliques))


@given(st.data())
def test_find_cliques_with_nodes_filters_to_maximal_cliques_containing_those_nodes(data):
    G = _draw_graph(data)
    all_cliques = list(networkx.find_cliques(G))

    if all_cliques:
        base_clique = data.draw(st.sampled_from(all_cliques))
        required_nodes = data.draw(
            st.lists(st.sampled_from(base_clique), unique=True)
        )
    else:
        required_nodes = []

    filtered_cliques = list(networkx.find_cliques(G, nodes=required_nodes))

    assert all(
        set(required_nodes).issubset(clique)
        for clique in map(set, filtered_cliques)
    )

    assert {
        frozenset(clique)
        for clique in filtered_cliques
    } == {
        frozenset(clique)
        for clique in all_cliques
        if set(required_nodes).issubset(clique)
    }
# End program