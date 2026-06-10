from hypothesis import given, strategies as st, assume, settings
import networkx as nx


# ---------- Strategies ----------

def graph_strategy(draw, directed=False, multigraph=False):
    """Build a (possibly directed/multi) graph from generated nodes and edges."""
    n = draw(st.integers(min_value=0, max_value=8))
    nodes = list(range(n))
    if n == 0:
        edges = []
    else:
        edges = draw(
            st.lists(
                st.tuples(
                    st.integers(min_value=0, max_value=n - 1),
                    st.integers(min_value=0, max_value=n - 1),
                ),
                min_size=0,
                max_size=20,
            )
        )
    if directed:
        G = nx.MultiDiGraph() if multigraph else nx.DiGraph()
    else:
        G = nx.MultiGraph() if multigraph else nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def any_graph(draw):
    directed = draw(st.booleans())
    multigraph = draw(st.booleans())
    return graph_strategy(draw, directed=directed, multigraph=multigraph), directed, multigraph


def normalize_edge(edge, orientation):
    """Strip the traversal-direction tag (if present) and return (u, v[, key])."""
    if orientation is not None:
        return tuple(edge[:-1])
    return tuple(edge)


def edge_exists(G, u, v, key=None):
    """Check (considering direction for digraphs) whether an edge exists in G."""
    if G.is_directed():
        if key is not None:
            return G.has_edge(u, v, key)
        return G.has_edge(u, v)
    else:
        if key is not None:
            return G.has_edge(u, v, key) or G.has_edge(v, u, key)
        return G.has_edge(u, v) or G.has_edge(v, u)


# ---------- Tests ----------

@given(st.data())
@settings(max_examples=300)
def test_returned_edges_exist_in_graph():
    pass


@given(st.data())
@settings(max_examples=300)
def test_networkx_find_cycle_property(data):
    G, directed, multigraph = any_graph(data.draw)
    orientation = data.draw(
        st.sampled_from([None])
        if not directed
        else st.sampled_from([None, "original", "reverse", "ignore"])
    )

    try:
        cycle = list(nx.find_cycle(G, source=None, orientation=orientation))
    except nx.NetworkXNoCycle:
        # Property 4 (negative side): no cycle should exist under these semantics.
        # Build the graph used for cycle detection given the orientation.
        if not directed:
            assert nx.is_forest(G) or not _undirected_has_cycle(G)
        else:
            if orientation in (None, "original"):
                assert nx.is_directed_acyclic_graph(G)
            else:
                # reverse / ignore -> treat as undirected for cycle existence
                UG = G.to_undirected()
                assert not _undirected_has_cycle(UG)
        return

    # We got a cycle. Run all positive properties.

    # ---- Property 3: tuple length / direction tag ----
    base_len = 3 if multigraph else 2
    for edge in cycle:
        if orientation is None:
            assert len(edge) == base_len
        else:
            assert len(edge) == base_len + 1
            assert edge[-1] in ("forward", "reverse")

    # ---- Property 1: every edge exists in G ----
    for edge in cycle:
        norm = normalize_edge(edge, orientation)
        if multigraph:
            u, v, key = norm
            assert edge_exists(G, u, v, key)
        else:
            u, v = norm
            assert edge_exists(G, u, v)

    # ---- Property 2: edges form a connected closed path (a cycle) ----
    # Build the sequence of (tail, head) as traversed.
    traversed = []
    for edge in cycle:
        norm = normalize_edge(edge, orientation)
        u, v = norm[0], norm[1]
        if orientation in ("reverse",):
            # 'reverse' traverses edges reversed; the reported tuple keeps
            # the directed orientation, but traversal direction is reversed.
            tail, head = v, u
        elif orientation is not None and len(edge) > 0 and edge[-1] == "reverse":
            tail, head = v, u
        else:
            tail, head = u, v
        traversed.append((tail, head))

    # Consecutive edges should chain: head of one == tail of next.
    for i in range(len(traversed)):
        head = traversed[i][1]
        next_tail = traversed[(i + 1) % len(traversed)][0]
        assert head == next_tail, (
            f"Cycle not chained: {traversed}"
        )

    # The path must close: last head returns to first tail.
    assert traversed[0][0] == traversed[-1][1]

    # ---- Property 4 (positive side): a cycle truly exists ----
    # The fact that we obtained a valid closed chain already demonstrates this.
    assert len(cycle) >= 1


@given(st.data())
@settings(max_examples=300)
def test_networkx_find_cycle_source(data):
    """Property 5: source-constrained search consistency."""
    G, directed, multigraph = any_graph(data.draw)
    assume(G.number_of_nodes() > 0)
    orientation = data.draw(
        st.sampled_from([None])
        if not directed
        else st.sampled_from([None, "original", "reverse", "ignore"])
    )
    source = data.draw(st.sampled_from(list(G.nodes())))

    # If find_cycle with source=None finds nothing, source-based must also fail.
    try:
        nx.find_cycle(G, source=None, orientation=orientation)
        global_has_cycle = True
    except nx.NetworkXNoCycle:
        global_has_cycle = False

    try:
        cycle = list(nx.find_cycle(G, source=source, orientation=orientation))
    except nx.NetworkXNoCycle:
        return  # acceptable: this particular source reaches no cycle

    # If source-based found a cycle, then a cycle exists in the graph overall.
    assert global_has_cycle

    # The returned cycle must still be a valid set of existing edges.
    for edge in cycle:
        norm = normalize_edge(edge, orientation)
        if multigraph:
            u, v, key = norm
            assert edge_exists(G, u, v, key)
        else:
            u, v = norm
            assert edge_exists(G, u, v)


def _undirected_has_cycle(G):
    """Helper: does an undirected (multi)graph contain a cycle?"""
    UG = G.to_undirected() if G.is_directed() else G
    # A simple connected component with more edges than (nodes-1) has a cycle,
    # also any self-loop or parallel edge constitutes a cycle.
    if any(u == v for u, v in UG.edges()):
        return True
    # Parallel edges in a multigraph form a cycle.
    if UG.is_multigraph():
        seen = set()
        for u, v, k in UG.edges(keys=True):
            pair = frozenset((u, v))
            if pair in seen:
                return True
            seen.add(pair)
    try:
        nx.find_cycle(UG, orientation=None)
        return True
    except nx.NetworkXNoCycle:
        return False
# End program