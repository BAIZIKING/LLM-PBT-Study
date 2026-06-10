from hypothesis import given, strategies as st
import networkx


def _manual_degrees(G, weight=None):
    degrees = {node: 0 for node in G.nodes}

    for u, v, data in G.edges(data=True):
        edge_value = data.get(weight, 1) if weight is not None else 1

        if u == v:
            degrees[u] += 2 * edge_value
        else:
            degrees[u] += edge_value
            degrees[v] += edge_value

    return degrees


@given(st.data())
def test_networkx_degree_property(data):
    graph_type = data.draw(
        st.sampled_from(
            [
                networkx.Graph,
                networkx.MultiGraph,
                networkx.DiGraph,
                networkx.MultiDiGraph,
            ]
        )
    )

    node_count = data.draw(st.integers(min_value=0, max_value=8))
    nodes = list(range(node_count))

    if node_count == 0:
        edges = []
    else:
        edges = data.draw(
            st.lists(
                st.tuples(
                    st.integers(min_value=0, max_value=node_count - 1),
                    st.integers(min_value=0, max_value=node_count - 1),
                    st.one_of(st.none(), st.integers(min_value=-20, max_value=20)),
                ),
                max_size=25,
            )
        )

    G = graph_type()
    G.add_nodes_from(nodes)

    for u, v, w in edges:
        if w is None:
            G.add_edge(u, v)
        else:
            G.add_edge(u, v, w=w)

    unweighted_expected = _manual_degrees(G)
    weighted_expected = _manual_degrees(G, weight="w")

    full_unweighted = dict(networkx.degree(G))
    full_weighted = dict(networkx.degree(G, weight="w"))

    assert set(full_unweighted) == set(G.nodes)
    assert set(full_weighted) == set(G.nodes)

    for node in G.nodes:
        assert full_unweighted[node] == unweighted_expected[node]
        assert full_weighted[node] == weighted_expected[node]

    if nodes:
        single_node = data.draw(st.sampled_from(nodes))
        assert networkx.degree(G, single_node) == unweighted_expected[single_node]
        assert networkx.degree(G, single_node, weight="w") == weighted_expected[single_node]

    if nodes:
        selected_nodes = data.draw(
            st.lists(st.sampled_from(nodes), unique=True, max_size=len(nodes))
        )
    else:
        selected_nodes = []

    outside_nodes = list(range(node_count, node_count + 3))
    nbunch = selected_nodes + outside_nodes

    nbunch_unweighted = dict(networkx.degree(G, nbunch))
    nbunch_weighted = dict(networkx.degree(G, nbunch, weight="w"))

    assert set(nbunch_unweighted) == set(selected_nodes)
    assert set(nbunch_weighted) == set(selected_nodes)

    for node in selected_nodes:
        assert nbunch_unweighted[node] == unweighted_expected[node]
        assert nbunch_weighted[node] == weighted_expected[node]

    assert sum(dict(networkx.degree(G)).values()) == 2 * G.number_of_edges()

    total_edge_weight = sum(data.get("w", 1) for _, _, data in G.edges(data=True))
    assert sum(dict(networkx.degree(G, weight="w")).values()) == 2 * total_edge_weight


# End program