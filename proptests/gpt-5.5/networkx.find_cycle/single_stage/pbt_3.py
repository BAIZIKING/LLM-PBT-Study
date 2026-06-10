from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate Graph/DiGraph/MultiGraph/MultiDiGraph instances with 0-6 integer nodes,
# random edges including self-loops and parallel edges for multigraphs, random valid sources
# of None/a node/a nonempty node list, and every documented orientation value. The test checks
# that find_cycle either raises NetworkXNoCycle or returns a nonempty closed cyclic edge path
# whose edge tuples have the documented shape, direction markers when required, and correspond
# to real edges in the generated graph.
@given(st.data())
def test_networkx_find_cycle(data):
    graph_cls = data.draw(
        st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]),
        label="graph_cls",
    )

    node_count = data.draw(st.integers(min_value=0, max_value=6), label="node_count")
    nodes = list(range(node_count))

    G = graph_cls()
    G.add_nodes_from(nodes)

    if nodes:
        edge_pairs = data.draw(
            st.lists(
                st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)),
                min_size=0,
                max_size=15,
            ),
            label="edge_pairs",
        )
        for u, v in edge_pairs:
            G.add_edge(u, v)

        source = data.draw(
            st.one_of(
                st.none(),
                st.sampled_from(nodes),
                st.lists(
                    st.sampled_from(nodes),
                    min_size=1,
                    max_size=len(nodes),
                    unique=True,
                ),
            ),
            label="source",
        )
    else:
        source = None

    orientation = data.draw(
        st.sampled_from([None, "original", "reverse", "ignore"]),
        label="orientation",
    )

    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
    except nx.NetworkXNoCycle:
        return

    assert isinstance(cycle, list)
    assert len(cycle) > 0

    is_multi = G.is_multigraph()
    is_directed = G.is_directed()
    base_len = 3 if is_multi else 2

    traversal_tails = []
    traversal_heads = []

    for edge in cycle:
        assert isinstance(edge, tuple)

        has_direction_marker = (
            len(edge) == base_len + 1 and edge[-1] in {"forward", "reverse"}
        )

        if is_directed and orientation is not None:
            assert has_direction_marker
        else:
            assert len(edge) == base_len or has_direction_marker

        if is_multi:
            u, v, key = edge[:3]
            assert G.has_edge(u, v, key)
        else:
            u, v = edge[:2]
            assert G.has_edge(u, v)

        if has_direction_marker and edge[-1] == "reverse":
            tail, head = v, u
        else:
            tail, head = u, v

        traversal_tails.append(tail)
        traversal_heads.append(head)

    for i in range(len(cycle)):
        assert traversal_heads[i] == traversal_tails[(i + 1) % len(cycle)]
# End program