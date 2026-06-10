from hypothesis import given, strategies as st, settings
import networkx
from networkx.exception import NetworkXNoCycle


@st.composite
def graphs(draw):
    n_nodes = draw(st.integers(min_value=1, max_value=15))
    nodes = list(range(n_nodes))

    directed = draw(st.booleans())
    multi = draw(st.booleans())

    if directed and multi:
        G = networkx.MultiDiGraph()
    elif directed:
        G = networkx.DiGraph()
    elif multi:
        G = networkx.MultiGraph()
    else:
        G = networkx.Graph()

    G.add_nodes_from(nodes)

    edges = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=n_nodes - 1),
                st.integers(min_value=0, max_value=n_nodes - 1),
            ),
            max_size=40,
        )
    )
    for u, v in edges:
        G.add_edge(u, v)

    return G


def _endpoints(edge, orientation):
    """Return (tail, head) of a returned cycle edge, respecting orientation."""
    u, v = edge[0], edge[1]
    if orientation is None:
        return u, v
    direction = edge[-1]
    if direction == 'reverse':
        return v, u
    return u, v


@given(st.data())
@settings(max_examples=300)
def test_networkx_find_cycle_property(data):
    G = data.draw(graphs())

    # Decide orientation (only valid choices for directed graphs include the markers)
    if G.is_directed():
        orientation = data.draw(
            st.sampled_from([None, "original", "reverse", "ignore"])
        )
    else:
        orientation = data.draw(st.sampled_from([None]))

    # Optionally choose a source node
    use_source = data.draw(st.booleans())
    source = None
    if use_source and G.number_of_nodes() > 0:
        source = data.draw(st.sampled_from(list(G.nodes())))

    try:
        cycle = list(networkx.find_cycle(G, source=source, orientation=orientation))
        found = True
    except NetworkXNoCycle:
        cycle = None
        found = False

    multi = G.is_multigraph()

    if found:
        # Property 1: non-empty list, consecutive edges connect, closes into a cycle
        assert len(cycle) >= 1
        endpoints = [_endpoints(e, orientation) for e in cycle]
        for i in range(len(endpoints) - 1):
            # head of current == tail of next
            assert endpoints[i][1] == endpoints[i + 1][0]
        # closes: head of last == tail of first
        assert endpoints[-1][1] == endpoints[0][0]

        # Property 2: every edge exists in the graph (respecting orientation)
        for e in cycle:
            u, v = e[0], e[1]
            if orientation == "ignore" or not G.is_directed():
                assert G.has_edge(u, v) or G.has_edge(v, u)
            else:
                # 'original', 'reverse', or None: (u, v) reported as actual directed edge
                assert G.has_edge(u, v)

        # Property 3: tuple lengths / direction marker
        base_len = 3 if multi else 2
        for e in cycle:
            if orientation is None:
                assert len(e) == base_len
            else:
                assert len(e) == base_len + 1
                assert e[-1] in ("forward", "reverse")

        # Property 4: if source given, source participates in the cycle
        if source is not None:
            cycle_nodes = set()
            for tail, head in endpoints:
                cycle_nodes.add(tail)
                cycle_nodes.add(head)
            assert source in cycle_nodes

        # Property 5: graph genuinely has a cycle under this orientation.
        # Verify consistency: re-running without source should also find a cycle.
        try:
            networkx.find_cycle(G, source=None, orientation=orientation)
        except NetworkXNoCycle:
            assert False, "Cycle found with source but not without source"

    else:
        # Property 5 (negative): If no cycle found at all (no source),
        # then searching from any source should also raise.
        if source is None:
            for node in G.nodes():
                try:
                    networkx.find_cycle(G, source=node, orientation=orientation)
                    assert False, "find_cycle from a node found a cycle though global search did not"
                except NetworkXNoCycle:
                    pass
# End program