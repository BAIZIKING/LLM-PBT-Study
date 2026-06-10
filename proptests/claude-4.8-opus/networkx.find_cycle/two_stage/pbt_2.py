from hypothesis import given, strategies as st, assume, settings
import networkx as nx


# Strategy to build a graph (directed or undirected, simple or multi) from edges
@st.composite
def graphs(draw, allow_directed=True, allow_multi=True):
    n_nodes = draw(st.integers(min_value=1, max_value=20))
    nodes = list(range(n_nodes))

    directed = draw(st.booleans()) if allow_directed else False
    multi = draw(st.booleans()) if allow_multi else False

    if directed and multi:
        G = nx.MultiDiGraph()
    elif directed:
        G = nx.DiGraph()
    elif multi:
        G = nx.MultiGraph()
    else:
        G = nx.Graph()

    G.add_nodes_from(nodes)

    n_edges = draw(st.integers(min_value=0, max_value=40))
    edges = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=n_nodes - 1),
                st.integers(min_value=0, max_value=n_nodes - 1),
            ),
            min_size=n_edges,
            max_size=n_edges,
        )
    )
    G.add_edges_from(edges)
    return G


orientations = st.sampled_from([None, "original", "reverse", "ignore"])


def edge_endpoints(edge, orientation):
    """Return (u, v) tail/head ignoring any direction tag and key."""
    # Strip a trailing direction tag if orientation is not None
    if orientation is not None:
        e = edge[:-1]
    else:
        e = edge
    u, v = e[0], e[1]
    return u, v


def get_traversal_uv(edge, orientation):
    """
    Return the (entry, exit) nodes of an edge as traversed,
    accounting for direction tags.
    """
    if orientation is not None:
        direction = edge[-1]
        u, v = edge[0], edge[1]
        if direction == "reverse":
            return v, u
        else:
            return u, v
    else:
        return edge[0], edge[1]


@given(st.data())
@settings(max_examples=500)
def test_networkx_find_cycle_property():
    data = st.data()

    @given(G=graphs(), orientation=orientations, use_source=st.booleans(), src=st.integers(min_value=0, max_value=19))
    @settings(max_examples=1)
    def inner(G, orientation, use_source, src):
        # Determine source
        source = None
        if use_source and G.number_of_nodes() > 0:
            source = src % G.number_of_nodes()

        is_multi = G.is_multigraph()

        try:
            if source is not None:
                cycle = list(nx.find_cycle(G, source=source, orientation=orientation))
            else:
                cycle = list(nx.find_cycle(G, orientation=orientation))
            found = True
        except nx.exception.NetworkXNoCycle:
            cycle = None
            found = False

        if found:
            assert len(cycle) > 0

            # Property 3: direction tag presence and edge tuple length
            base_len = 3 if is_multi else 2
            for edge in cycle:
                if orientation is None:
                    assert len(edge) == base_len
                else:
                    assert len(edge) == base_len + 1
                    assert edge[-1] in ("forward", "reverse")

            # Property 2: every edge exists in G
            for edge in cycle:
                u, v = edge_endpoints(edge, orientation)
                if is_multi:
                    key = edge[2]
                    assert G.has_edge(u, v) or (not G.is_directed() and G.has_edge(v, u))
                    # Verify key exists in some orientation
                    ok = (G.has_edge(u, v) and key in G[u][v]) or (
                        not G.is_directed() and G.has_edge(v, u) and key in G[v][u]
                    )
                    assert ok
                else:
                    assert G.has_edge(u, v) or (not G.is_directed() and G.has_edge(v, u))

            # Property 1: edges form a closed path (using traversal entry/exit)
            traversal = [get_traversal_uv(edge, orientation) for edge in cycle]
            for i in range(len(traversal)):
                cur_exit = traversal[i][1]
                next_entry = traversal[(i + 1) % len(traversal)][0]
                assert cur_exit == next_entry, (
                    f"Path not closed: {traversal}"
                )

            # Property 4: if source provided, it must appear in the cycle
            if source is not None:
                nodes_in_cycle = set()
                for edge in cycle:
                    u, v = edge_endpoints(edge, orientation)
                    nodes_in_cycle.add(u)
                    nodes_in_cycle.add(v)
                assert source in nodes_in_cycle

        else:
            # Property 5: NetworkXNoCycle => graph is acyclic under the given
            # orientation (and reachable region from source, if specified).
            # Verify that an independent cycle check agrees.
            if source is None:
                if orientation == "ignore" and G.is_directed():
                    # treat as undirected
                    UG = G.to_undirected()
                    has_cycle = True
                    try:
                        nx.find_cycle(UG)
                    except nx.exception.NetworkXNoCycle:
                        has_cycle = False
                    assert not has_cycle
                elif orientation == "reverse" and G.is_directed():
                    RG = G.reverse(copy=True)
                    has_cycle = True
                    try:
                        nx.find_cycle(RG, orientation="original")
                    except nx.exception.NetworkXNoCycle:
                        has_cycle = False
                    assert not has_cycle
                elif G.is_directed():
                    # original or None on directed graph => must be a DAG
                    assert nx.is_directed_acyclic_graph(G)
                else:
                    # undirected graph: no cycle means it's a forest
                    assert nx.is_forest(G)

    inner()
# End program