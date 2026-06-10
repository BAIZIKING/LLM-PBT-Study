from hypothesis import given, settings, strategies as st
import networkx as nx


# Strategy to build a graph (directed or undirected, possibly multigraph)
@st.composite
def graphs(draw):
    n_nodes = draw(st.integers(min_value=1, max_value=15))
    nodes = list(range(n_nodes))

    directed = draw(st.booleans())
    multigraph = draw(st.booleans())

    if directed and multigraph:
        G = nx.MultiDiGraph()
    elif directed:
        G = nx.DiGraph()
    elif multigraph:
        G = nx.MultiGraph()
    else:
        G = nx.Graph()

    G.add_nodes_from(nodes)

    # generate edges
    possible_edges = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=n_nodes - 1),
                st.integers(min_value=0, max_value=n_nodes - 1),
            ),
            min_size=0,
            max_size=40,
        )
    )
    for u, v in possible_edges:
        G.add_edge(u, v)

    return G, directed, multigraph


def _normalize_edge(edge, orientation):
    """Return (u, v, key_or_none, direction_or_none) from a yielded edge tuple."""
    direction = None
    if orientation is not None:
        direction = edge[-1]
        core = edge[:-1]
    else:
        core = edge
    if len(core) == 3:
        u, v, key = core
    else:
        u, v = core
        key = None
    return u, v, key, direction


def _edge_exists(G, u, v, key, multigraph):
    if multigraph:
        return G.has_edge(u, v, key)
    else:
        return G.has_edge(u, v)


@given(graphs(), st.sampled_from([None, "original", "reverse", "ignore"]))
@settings(max_examples=300)
def test_networkx_find_cycle_property(graph_bundle, orientation):
    G, directed, multigraph = graph_bundle

    # orientation only valid for directed graphs; for undirected, only None applies
    if not directed:
        orientation = None

    # Decide on optional source
    nodes = list(G.nodes())

    try:
        result = list(nx.find_cycle(G, orientation=orientation))
        found_cycle = True
    except nx.NetworkXNoCycle:
        result = None
        found_cycle = False

    if not found_cycle:
        # Property 5 (converse): no cycle should exist under this orientation.
        # We verify by checking that no cycle can be found at all.
        # Build the effective graph to check for cycles.
        if orientation in (None, "original"):
            check_G = G
        elif orientation == "reverse":
            check_G = G.reverse(copy=True) if directed else G
        elif orientation == "ignore":
            check_G = G.to_undirected()
        else:
            check_G = G

        # If a cycle truly existed, find_cycle would have found it.
        # So assert that there's no cycle in check_G consistent with the claim.
        try:
            # cycle_basis / simple_cycles depending on type
            if check_G.is_directed():
                has_cycle = len(list(nx.simple_cycles(check_G))) > 0
                # self loops also count
                has_self_loop = any(u == v for u, v in nx.selfloop_edges(check_G))
                assert not (has_cycle or has_self_loop)
            else:
                # undirected: a cycle exists iff edges >= nodes in some component,
                # use cycle_basis
                has_cycle = len(nx.cycle_basis(check_G)) > 0
                has_self_loop = any(u == v for u, v in nx.selfloop_edges(check_G))
                # multigraph parallel edges form a cycle
                has_parallel = False
                if check_G.is_multigraph():
                    seen = set()
                    for u, v in check_G.edges():
                        key2 = frozenset((u, v))
                        if key2 in seen and u != v:
                            has_parallel = True
                        seen.add(key2)
                assert not (has_cycle or has_self_loop or has_parallel)
        except nx.NetworkXError:
            pass
        return

    # A cycle was found.
    assert len(result) > 0

    normalized = [_normalize_edge(e, orientation) for e in result]

    # Property 3: direction indicator presence
    for (u, v, key, direction) in normalized:
        if orientation is None:
            assert direction is None
        else:
            assert direction in ("forward", "reverse")

    # Property 1: every returned edge must be an actual edge in G (respecting orientation)
    for (u, v, key, direction) in normalized:
        if orientation is None or orientation == "original":
            # edge as directed/undirected must exist
            assert _edge_exists(G, u, v, key, multigraph)
        elif orientation == "reverse":
            # the reported (u, v) is in actual directed order, but traversed reverse.
            # The actual edge (u, v) must exist in G.
            assert _edge_exists(G, u, v, key, multigraph)
        elif orientation == "ignore":
            # treat as undirected: either (u,v) or (v,u) exists
            exists = _edge_exists(G, u, v, key, multigraph) or _edge_exists(
                G, v, u, key, multigraph
            )
            assert exists

    # Property 2: edges form a contiguous closed path under traversal direction.
    # Compute the traversal tail/head per edge.
    traversal = []
    for (u, v, key, direction) in normalized:
        if direction == "reverse":
            traversal.append((v, u))
        else:
            traversal.append((u, v))

    # contiguous: head of each matches tail of next
    for i in range(len(traversal)):
        head = traversal[i][1]
        next_tail = traversal[(i + 1) % len(traversal)][0]
        assert head == next_tail

    # Property 4: if source specified and appears, it's in the cycle nodes.
    # (Here we did not pass an explicit source; test it separately below.)


@given(graphs(), st.sampled_from([None, "original", "reverse", "ignore"]), st.data())
@settings(max_examples=200)
def test_networkx_find_cycle_source_property(graph_bundle, orientation, data):
    G, directed, multigraph = graph_bundle
    if not directed:
        orientation = None

    nodes = list(G.nodes())
    if not nodes:
        return

    source = data.draw(st.sampled_from(nodes))

    try:
        result = list(nx.find_cycle(G, source=source, orientation=orientation))
    except nx.NetworkXNoCycle:
        return

    normalized = [_normalize_edge(e, orientation) for e in result]

    # Property 4: the source node must appear among the nodes in the cycle.
    cycle_nodes = set()
    for (u, v, key, direction) in normalized:
        cycle_nodes.add(u)
        cycle_nodes.add(v)
    assert source in cycle_nodes
# End program