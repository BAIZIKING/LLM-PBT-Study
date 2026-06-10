from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random graphs of all 4 networkx types with random nodes,
# edges (sometimes injecting a guaranteed cycle), and random source/orientation.
# Verify that any returned cycle is a valid chained cycle whose edges exist in
# the graph, that tuple formats match the orientation/multigraph rules, and that
# raised NetworkXNoCycle is consistent with the graph structure.
@given(st.data())
def test_networkx_find_cycle(data):
    # --- Choose graph type ---
    graph_cls = data.draw(st.sampled_from(
        [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
    ))
    G = graph_cls()
    is_directed = G.is_directed()
    is_multi = G.is_multigraph()

    # --- Nodes ---
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=8),
                               unique=True, max_size=8))
    G.add_nodes_from(nodes)

    # --- Edges ---
    if nodes:
        edges = data.draw(st.lists(
            st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)),
            max_size=15))
        G.add_edges_from(edges)

        # Occasionally inject a guaranteed cycle
        if data.draw(st.booleans()) and len(nodes) >= 2:
            cyc = data.draw(st.lists(st.sampled_from(nodes),
                                     min_size=2, max_size=len(nodes),
                                     unique=True))
            for i in range(len(cyc)):
                G.add_edge(cyc[i], cyc[(i + 1) % len(cyc)])

    # --- Source ---
    source_choice = data.draw(st.sampled_from(["none", "node", "outside"]))
    if source_choice == "none" or not nodes:
        source = None
    elif source_choice == "node":
        source = data.draw(st.sampled_from(nodes))
    else:
        source = 999  # node not in graph

    # --- Orientation ---
    if is_directed:
        orientation = data.draw(st.sampled_from(
            [None, "original", "reverse", "ignore"]))
    else:
        # orientation only meaningful for directed graphs
        orientation = data.draw(st.sampled_from([None, "ignore"]))

    # --- Call function ---
    try:
        result = list(nx.find_cycle(G, source=source, orientation=orientation))
    except nx.NetworkXNoCycle:
        # Consistency: for orientation 'ignore', no undirected cycle should exist
        # in the (reachable) graph. We verify the global claim: if there is truly
        # no cycle at all, then the undirected projection must be a forest.
        if source is None and orientation == "ignore":
            assert nx.is_forest(nx.Graph(G.to_undirected())), \
                "No cycle reported but undirected graph has a cycle"
        return
    except nx.NodeNotFound:
        # Acceptable when source node is not in the graph
        return

    # --- A cycle was returned: validate it ---
    assert len(result) >= 1, "A returned cycle must contain at least one edge"

    # Determine expected tuple length
    # base: (u, v); +1 for multigraph key; +1 for orientation tag (if not None)
    expected_len = 2
    if is_multi:
        expected_len += 1
    if orientation is not None:
        expected_len += 1

    parsed = []  # list of (tail, head) in traversal order
    for edge in result:
        assert len(edge) == expected_len, (
            f"Edge {edge} has length {len(edge)}, expected {expected_len}")

        # Strip the orientation tag if present
        if orientation is not None:
            direction = edge[-1]
            assert direction in ("forward", "reverse"), \
                f"Invalid direction tag: {direction}"
            core = edge[:-1]
        else:
            core = edge

        # core is (u, v) or (u, v, key)
        u, v = core[0], core[1]

        # Verify the edge actually exists in the graph (respecting direction
        # of traversal). For undirected graphs, has_edge is symmetric.
        if orientation == "reverse":
            # edge stored as (u, v) but traversed reverse -> check graph has (u,v)
            assert G.has_edge(u, v) or G.has_edge(v, u), \
                f"Edge {(u, v)} not in graph"
        else:
            assert G.has_edge(u, v) or G.has_edge(v, u), \
                f"Edge {(u, v)} not in graph"

        # For traversal chaining, compute the actual (tail, head) as walked.
        if orientation is not None and edge[-1] == "reverse":
            parsed.append((v, u))
        else:
            parsed.append((u, v))

    # --- Validate that parsed edges form a cycle (chain head-to-tail) ---
    # Consecutive edges should connect: head of one == tail of next
    for i in range(len(parsed)):
        cur_head = parsed[i][1]
        nxt_tail = parsed[(i + 1) % len(parsed)][0]
        assert cur_head == nxt_tail, (
            f"Cycle edges do not chain: edge {parsed[i]} head {cur_head} "
            f"!= next tail {nxt_tail}")
# End program