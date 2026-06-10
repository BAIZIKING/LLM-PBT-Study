from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random directed/undirected (multi)graphs from random edge lists,
# choose a valid source (or None) and a random orientation. Verify that find_cycle
# either raises NetworkXNoCycle, or returns a valid cycle whose edges exist in the
# graph, connect head-to-tail (respecting traversal direction), close into a loop,
# and carry proper direction labels when orientation is not None.
@given(st.data())
def test_networkx_find_cycle(data):
    # Choose graph type
    graph_cls = data.draw(st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]))
    directed = graph_cls in (nx.DiGraph, nx.MultiDiGraph)
    multi = graph_cls in (nx.MultiGraph, nx.MultiDiGraph)

    # Generate random edges from a small pool of nodes
    nodes = list(range(data.draw(st.integers(min_value=0, max_value=6))))
    if nodes:
        edges = data.draw(st.lists(
            st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)),
            min_size=0, max_size=12,
        ))
    else:
        edges = []

    G = graph_cls()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Choose source: None or a valid node
    if nodes:
        source = data.draw(st.one_of(st.none(), st.sampled_from(nodes)))
    else:
        source = None

    # Choose orientation (only meaningful for directed graphs, but allowed otherwise)
    if directed:
        orientation = data.draw(st.sampled_from([None, "original", "reverse", "ignore"]))
    else:
        orientation = None

    try:
        result = list(nx.find_cycle(G, source=source, orientation=orientation))
    except nx.NetworkXNoCycle:
        # Acceptable outcome: no cycle was found.
        return

    # A returned cycle must be a non-empty list of edges.
    assert isinstance(result, list)
    assert len(result) >= 1

    # Helper to parse an edge tuple based on graph type and orientation.
    def parse(edge):
        e = list(edge)
        direction = None
        if orientation is not None:
            direction = e[-1]
            assert direction in ("forward", "reverse")
            e = e[:-1]
        if multi:
            u, v, key = e[0], e[1], e[2]
        else:
            u, v = e[0], e[1]
            key = None
        return u, v, key, direction

    # Determine, for each reported edge, the (tail, head) actually traversed,
    # and verify the underlying edge exists in G.
    traversal = []
    for edge in result:
        u, v, key, direction = parse(edge)

        # The reported (u, v) must correspond to a real edge in G.
        if multi:
            assert G.has_edge(u, v, key), f"Edge {(u, v, key)} not in graph"
        else:
            assert G.has_edge(u, v), f"Edge {(u, v)} not in graph"

        # Determine the direction of traversal (which node we entered from / exited to).
        if orientation == "reverse":
            # Edge traversed against its reported direction.
            tail, head = v, u
        elif orientation == "ignore":
            # Traversal direction given by 'forward'/'reverse' relative to (u, v).
            tail, head = (u, v) if direction == "forward" else (v, u)
        else:
            # None or "original": traversal follows reported (u, v).
            tail, head = u, v
        traversal.append((tail, head))

    # The traversal edges must chain head-to-tail and close into a cycle.
    for i in range(len(traversal)):
        head = traversal[i][1]
        next_tail = traversal[(i + 1) % len(traversal)][0]
        assert head == next_tail, (
            f"Cycle not contiguous: edge {traversal[i]} head does not match "
            f"next tail {next_tail}"
        )
# End program