from hypothesis import given, strategies as st
import networkx as nx
from networkx.exception import NetworkXNoCycle, NetworkXError, NodeNotFound

# Summary: Generate directed/undirected (multi)graphs over a small node pool to
# encourage cycles and edge cases (self-loops, parallel edges, empty graphs),
# pair them with varied source (None/valid/list/invalid) and orientation values,
# then verify that find_cycle either returns a structurally valid cycle whose
# edges exist in G or raises NetworkXNoCycle, with correct tuple shapes per the docs.
@given(st.data())
def test_networkx_find_cycle(data):
    # Choose graph class
    graph_cls = data.draw(st.sampled_from([
        nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph
    ]))
    is_directed = graph_cls in (nx.DiGraph, nx.MultiDiGraph)
    is_multi = graph_cls in (nx.MultiGraph, nx.MultiDiGraph)

    nodes = list(range(7))
    edges = data.draw(st.lists(
        st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)),
        min_size=0, max_size=15,
    ))

    G = graph_cls()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Choose orientation
    if is_directed:
        orientation = data.draw(st.sampled_from([None, "original", "reverse", "ignore"]))
    else:
        orientation = data.draw(st.sampled_from([None, "ignore"]))

    # Choose source
    source_kind = data.draw(st.sampled_from(["none", "node", "list", "invalid"]))
    if source_kind == "none":
        source = None
    elif source_kind == "node":
        source = data.draw(st.sampled_from(nodes))
    elif source_kind == "list":
        source = data.draw(st.lists(st.sampled_from(nodes), min_size=1, max_size=3))
    else:
        source = 999  # node not in graph

    try:
        result = nx.find_cycle(G, source=source, orientation=orientation)
    except NetworkXNoCycle:
        # Valid outcome: no cycle found. Nothing more to assert.
        return
    except (NodeNotFound, NetworkXError):
        # Invalid source node may legitimately raise; ignore these cases.
        return

    # Result must be a list of edge tuples
    result = list(result)
    assert len(result) >= 1, "A found cycle must contain at least one edge"

    # Determine expected base tuple length (2 for graphs, 3 for multigraphs)
    base_len = 3 if is_multi else 2
    # If orientation is not None, tuple is extended with a direction string
    expected_len = base_len + (1 if orientation is not None else 0)

    for edge in result:
        assert isinstance(edge, tuple)
        assert len(edge) == expected_len, (
            f"Edge {edge} has length {len(edge)}, expected {expected_len}"
        )
        if orientation is not None:
            direction = edge[-1]
            assert direction in ("forward", "reverse"), (
                f"Direction tag {direction!r} not in expected set"
            )
            u, v = edge[0], edge[1]
        else:
            u, v = edge[0], edge[1]

        # Endpoints must be real nodes in G
        assert u in G, f"Tail {u} of edge not in graph"
        assert v in G, f"Head {v} of edge not in graph"
        # The underlying edge must exist in G
        assert G.has_edge(u, v), f"Edge ({u}, {v}) does not exist in G"

    # Verify the result forms a connected cyclic path.
    # Build the sequence of (tail, head) as actually traversed.
    def traversed_endpoints(edge):
        u, v = edge[0], edge[1]
        if orientation is not None:
            direction = edge[-1]
            # 'reverse' means the edge was traversed from v to u
            if direction == "reverse":
                return v, u
            return u, v
        # No orientation reported: for undirected graphs traversal direction
        # is as given; for directed graphs edges respect actual direction.
        return u, v

    traversal = [traversed_endpoints(e) for e in result]

    # For undirected graphs (or ignore orientation), an edge can be walked in
    # either direction. To robustly check connectivity, verify that consecutive
    # edges share a node, and that the path closes into a cycle.
    if orientation in (None,) and not is_directed:
        # Undirected: just confirm consecutive edges share a vertex and it closes.
        all_nodes_seq = []
        for (a, b) in traversal:
            all_nodes_seq.append((a, b))
        # Check chain connectivity allowing either endpoint to connect.
        for i in range(len(all_nodes_seq)):
            a, b = all_nodes_seq[i]
            na, nb = all_nodes_seq[(i + 1) % len(all_nodes_seq)]
            shared = len({a, b} & {na, nb}) > 0
            assert shared, f"Edges {all_nodes_seq[i]} and {all_nodes_seq[(i+1)%len(all_nodes_seq)]} not connected"
    else:
        # Directed-style traversal: head of one edge == tail of next, and closes.
        for i in range(len(traversal)):
            _, head = traversal[i]
            next_tail, _ = traversal[(i + 1) % len(traversal)]
            assert head == next_tail, (
                f"Cycle not contiguous: edge {traversal[i]} head {head} "
                f"!= next tail {next_tail}"
            )
# End program