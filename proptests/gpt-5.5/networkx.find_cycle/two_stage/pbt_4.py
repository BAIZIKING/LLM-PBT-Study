from hypothesis import given, strategies as st
import networkx


@st.composite
def _graph_source_orientation(draw):
    graph_class = draw(
        st.sampled_from(
            [
                networkx.Graph,
                networkx.DiGraph,
                networkx.MultiGraph,
                networkx.MultiDiGraph,
            ]
        )
    )

    node_count = draw(st.integers(min_value=0, max_value=8))
    nodes = list(range(node_count))

    G = graph_class()
    G.add_nodes_from(nodes)

    edge_count = draw(st.integers(min_value=0, max_value=20 if node_count else 0))
    for _ in range(edge_count):
        u = draw(st.sampled_from(nodes))
        v = draw(st.sampled_from(nodes))
        G.add_edge(u, v)

    if G.is_directed():
        orientation = draw(st.sampled_from([None, "original", "reverse", "ignore"]))
    else:
        orientation = None

    if node_count == 0:
        source = None
    else:
        source = draw(
            st.one_of(
                st.none(),
                st.sampled_from(nodes),
                st.lists(st.sampled_from(nodes), min_size=0, max_size=node_count),
            )
        )

    return G, source, orientation


def _find_cycle_or_none(G, source, orientation):
    try:
        return networkx.find_cycle(G, source=source, orientation=orientation)
    except networkx.exception.NetworkXNoCycle:
        return None


def _parse_edge(G, edge, orientation):
    if G.is_multigraph():
        if G.is_directed() and orientation is not None:
            assert len(edge) == 4
            u, v, key, direction = edge
        else:
            assert len(edge) == 3
            u, v, key = edge
            direction = None
    else:
        if G.is_directed() and orientation is not None:
            assert len(edge) == 3
            u, v, direction = edge
            key = None
        else:
            assert len(edge) == 2
            u, v = edge
            key = None
            direction = None

    return u, v, key, direction


def _traversal_endpoints(G, edge, orientation):
    u, v, key, direction = _parse_edge(G, edge, orientation)

    if G.is_directed() and orientation is not None and direction == "reverse":
        return v, u

    return u, v


@given(_graph_source_orientation())
def test_networkx_find_cycle_returns_non_empty_list_when_cycle_found(args):
    G, source, orientation = args
    cycle = _find_cycle_or_none(G, source, orientation)

    if cycle is None:
        return

    assert isinstance(cycle, list)
    assert len(cycle) > 0


@given(_graph_source_orientation())
def test_networkx_find_cycle_edges_exist_in_graph(args):
    G, source, orientation = args
    cycle = _find_cycle_or_none(G, source, orientation)

    if cycle is None:
        return

    for edge in cycle:
        u, v, key, direction = _parse_edge(G, edge, orientation)

        if G.is_multigraph():
            assert G.has_edge(u, v, key)
        else:
            assert G.has_edge(u, v)


@given(_graph_source_orientation())
def test_networkx_find_cycle_edges_form_closed_traversal_path(args):
    G, source, orientation = args
    cycle = _find_cycle_or_none(G, source, orientation)

    if cycle is None:
        return

    traversal_edges = [
        _traversal_endpoints(G, edge, orientation)
        for edge in cycle
    ]

    for (_, head), (next_tail, _) in zip(
        traversal_edges,
        traversal_edges[1:] + traversal_edges[:1],
    ):
        assert head == next_tail


@given(_graph_source_orientation())
def test_networkx_find_cycle_edge_tuple_shape_matches_graph_type(args):
    G, source, orientation = args
    cycle = _find_cycle_or_none(G, source, orientation)

    if cycle is None:
        return

    for edge in cycle:
        if G.is_multigraph():
            if G.is_directed() and orientation is not None:
                assert len(edge) == 4
                assert edge[-1] in {"forward", "reverse"}
            else:
                assert len(edge) == 3
        else:
            if G.is_directed() and orientation is not None:
                assert len(edge) == 3
                assert edge[-1] in {"forward", "reverse"}
            else:
                assert len(edge) == 2


@given(_graph_source_orientation())
def test_networkx_find_cycle_orientation_markers_are_consistent(args):
    G, source, orientation = args
    cycle = _find_cycle_or_none(G, source, orientation)

    if cycle is None:
        return

    for edge in cycle:
        u, v, key, direction = _parse_edge(G, edge, orientation)

        if not G.is_directed() or orientation is None:
            assert direction is None
            continue

        assert direction in {"forward", "reverse"}

        if orientation == "original":
            assert direction == "forward"
        elif orientation == "reverse":
            assert direction == "reverse"
        elif orientation == "ignore":
            assert direction in {"forward", "reverse"}


# End program