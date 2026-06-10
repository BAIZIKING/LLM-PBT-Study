from hypothesis import given, strategies as st
import networkx


def _edge_subset_strategy(possible_edges):
    if not possible_edges:
        return st.just([])
    return st.lists(
        st.sampled_from(possible_edges),
        unique=True,
        max_size=min(20, len(possible_edges)),
    )


@st.composite
def _bounded_graph(draw, min_nodes=0, max_nodes=8, weighted=False):
    graph_kind = draw(st.sampled_from(["graph", "digraph"]))
    node_count = draw(st.integers(min_value=min_nodes, max_value=max_nodes))
    nodes = list(range(node_count))

    if graph_kind == "graph":
        G = networkx.Graph()
        possible_edges = [(u, v) for u in nodes for v in nodes if u <= v]
    else:
        G = networkx.DiGraph()
        possible_edges = [(u, v) for u in nodes for v in nodes]

    G.add_nodes_from(nodes)
    edges = draw(_edge_subset_strategy(possible_edges))

    for u, v in edges:
        if weighted:
            edge_weight = draw(st.one_of(st.none(), st.integers(min_value=-20, max_value=20)))
            if edge_weight is None:
                G.add_edge(u, v)
            else:
                G.add_edge(u, v, capacity=edge_weight)
        else:
            G.add_edge(u, v)

    return G


@given(st.data())
def test_networkx_degree_all_nodes_property(data):
    G = data.draw(_bounded_graph())

    degree_items = list(networkx.degree(G))
    degree_nodes = [node for node, degree in degree_items]

    assert len(degree_items) == G.number_of_nodes()
    assert set(degree_nodes) == set(G.nodes)
    assert all(node in G for node in degree_nodes)


@given(st.data())
def test_networkx_degree_nbunch_collection_property(data):
    G = data.draw(_bounded_graph())
    nbunch = data.draw(st.lists(st.integers(min_value=-5, max_value=15), max_size=20))

    degree_items = list(networkx.degree(G, nbunch=nbunch))
    degree_nodes = [node for node, degree in degree_items]

    assert all(node in nbunch for node in degree_nodes)
    assert all(node in G for node in degree_nodes)
    assert set(degree_nodes) == (set(nbunch) & set(G.nodes))


@given(st.data())
def test_networkx_degree_single_node_property(data):
    G = data.draw(_bounded_graph(min_nodes=1))
    node = data.draw(st.sampled_from(list(G.nodes)))

    degree_value = networkx.degree(G, nbunch=node)

    assert isinstance(degree_value, int)
    assert degree_value == G.degree[node]


@given(st.data())
def test_networkx_degree_unweighted_counts_incident_edges_property(data):
    G = data.draw(_bounded_graph(weighted=False))

    degrees = dict(networkx.degree(G, weight=None))

    for node in G.nodes:
        expected_degree = sum(
            (1 if u == node else 0) + (1 if v == node else 0)
            for u, v in G.edges()
        )

        assert isinstance(degrees[node], int)
        assert degrees[node] >= 0
        assert degrees[node] == expected_degree


@given(st.data())
def test_networkx_degree_weighted_sum_property(data):
    G = data.draw(_bounded_graph(weighted=True))

    degrees = dict(networkx.degree(G, weight="capacity"))

    for node in G.nodes:
        expected_degree = sum(
            ((1 if u == node else 0) + (1 if v == node else 0))
            * edge_data.get("capacity", 1)
            for u, v, edge_data in G.edges(data=True)
        )

        assert degrees[node] == expected_degree


# End program