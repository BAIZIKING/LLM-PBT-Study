from hypothesis import given, settings, strategies as st
import networkx
from networkx.exception import NetworkXNoCycle


# Strategy to build a graph (possibly directed/multigraph) with bounded nodes/edges
def graph_strategy(draw):
    n_nodes = draw(st.integers(min_value=1, max_value=8))
    nodes = list(range(n_nodes))

    directed = draw(st.booleans())
    multigraph = draw(st.booleans())

    if directed and multigraph:
        G = networkx.MultiDiGraph()
    elif directed:
        G = networkx.DiGraph()
    elif multigraph:
        G = networkx.MultiGraph()
    else:
        G = networkx.Graph()

    G.add_nodes_from(nodes)

    n_edges = draw(st.integers(min_value=0, max_value=20))
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
    for u, v in edges:
        G.add_edge(u, v)

    return G, directed, multigraph, nodes


def orientation_strategy(directed):
    if directed:
        return st.sampled_from([None, "original", "reverse", "ignore"])
    else:
        return st.just(None)


def edge_exists(G, directed, multigraph, u, v):
    """Check if an edge u->v (or undirected u-v) exists."""
    if directed:
        return G.has_edge(u, v)
    else:
        return G.has_edge(u, v) or G.has_edge(v, u)


def get_cycle(G, source, orientation):
    return list(networkx.find_cycle(G, source=source, orientation=orientation))


@given(st.data())
@settings(max_examples=300)
def test_networkx_find_cycle_property():
    data = st.data()  # placeholder, real data passed below

    # We use a single @given(st.data()) and draw everything inside.
    @given(st.data())
    def _inner(d):
        G, directed, multigraph, nodes = graph_strategy(d.draw)
        orientation = d.draw(orientation_strategy(directed))
        use_source = d.draw(st.booleans())
        source = d.draw(st.sampled_from(nodes)) if use_source and nodes else None

        try:
            cycle = get_cycle(G, source, orientation)
        except NetworkXNoCycle:
            # Property 5 (negative side): exception raised means no cycle found.
            return

        # If we reach here, a cycle was returned.

        # Property 1: non-empty list of edges forming a closed connected path.
        assert isinstance(cycle, list)
        assert len(cycle) > 0

        # Extract (tail, head) traversal endpoints for each edge.
        # Determine tuple layout: with orientation set, last element is direction.
        # With multigraph there is a key element.
        traversal = []
        for edge in cycle:
            edge = tuple(edge)
            if orientation is not None:
                # Property 3: last entry is a direction indicator.
                direction = edge[-1]
                assert direction in ("forward", "reverse")
                core = edge[:-1]
            else:
                # Property 3: no direction indicator (length is 2 or 3 for multigraph).
                core = edge

            if multigraph:
                # core is (u, v, key)
                assert len(core) == 3
                u, v, key = core
            else:
                assert len(core) == 2
                u, v = core

            # Determine the actual traversal direction (tail -> head).
            if orientation is not None:
                if direction == "forward":
                    tail, head = u, v
                else:  # reverse
                    tail, head = v, u
            else:
                tail, head = u, v

            traversal.append((tail, head))

        # Property 1: consecutive edges connect head->tail and cycle closes.
        for i in range(len(traversal)):
            cur_head = traversal[i][1]
            next_tail = traversal[(i + 1) % len(traversal)][0]
            assert cur_head == next_tail

        # Property 2: every edge corresponds to an actual edge in G respecting orientation.
        for edge in cycle:
            edge = tuple(edge)
            if orientation is not None:
                direction = edge[-1]
                core = edge[:-1]
            else:
                direction = None
                core = edge

            if multigraph:
                u, v, key = core
            else:
                u, v = core

            if not directed:
                assert edge_exists(G, directed, multigraph, u, v)
            else:
                if orientation in (None, "original"):
                    # u->v must be a real directed edge
                    assert G.has_edge(u, v)
                elif orientation == "reverse":
                    # edge tuple is in actual directed order u->v
                    assert G.has_edge(u, v)
                elif orientation == "ignore":
                    # actual directed edge exists in one of the orders
                    assert G.has_edge(u, v) or G.has_edge(v, u)

    _inner()
# End program