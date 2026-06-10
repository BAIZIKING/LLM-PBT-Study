from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random graphs of various types (Graph, DiGraph, MultiGraph,
# MultiDiGraph) from random node/edge sets, with random source and orientation.
# Verify that find_cycle either returns a valid list of cycle edges (correct
# tuple shape, edges exist in graph, edges chain into a closed loop) or raises
# NetworkXNoCycle.
@given(st.data())
def test_networkx_find_cycle(data):
    # Choose graph type
    graph_cls = data.draw(st.sampled_from(
        [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
    ))
    is_multi = graph_cls in (nx.MultiGraph, nx.MultiDiGraph)
    is_directed = graph_cls in (nx.DiGraph, nx.MultiDiGraph)

    # Generate nodes
    num_nodes = data.draw(st.integers(min_value=0, max_value=6))
    nodes = list(range(num_nodes))

    # Generate edges (allow self-loops and parallel edges)
    if num_nodes > 0:
        edges = data.draw(st.lists(
            st.tuples(
                st.sampled_from(nodes),
                st.sampled_from(nodes),
            ),
            min_size=0, max_size=12,
        ))
    else:
        edges = []

    G = graph_cls()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Choose source
    source = data.draw(st.one_of(
        st.none(),
        st.sampled_from(nodes) if num_nodes > 0 else st.none(),
    ))

    # Choose orientation (orientation only meaningful for directed graphs,
    # but the function accepts it generally; for undirected, non-None may error,
    # so restrict non-None orientations to directed graphs).
    if is_directed:
        orientation = data.draw(st.sampled_from(
            [None, 'original', 'reverse', 'ignore']
        ))
    else:
        orientation = None

    try:
        result = nx.find_cycle(G, source=source, orientation=orientation)
    except nx.NetworkXNoCycle:
        # Acceptable documented outcome: no cycle found.
        return
    except nx.NodeNotFound:
        # source not in graph component traversal edge-case; acceptable.
        return

    # Property 1: result is a list of edges
    result = list(result)
    assert isinstance(result, list)
    assert len(result) >= 1, "A reported cycle must contain at least one edge"

    # Property 2: tuple shape correctness
    has_direction = orientation is not None
    expected_core_len = 3 if is_multi else 2
    expected_len = expected_core_len + (1 if has_direction else 0)

    for edge in result:
        assert isinstance(edge, tuple)
        assert len(edge) == expected_len, (
            f"Edge {edge} has wrong length; expected {expected_len}"
        )
        if has_direction:
            assert edge[-1] in ('forward', 'reverse')

    # Property 3: every reported edge actually exists in the graph
    for edge in result:
        u, v = edge[0], edge[1]
        assert G.has_edge(u, v), f"Reported edge ({u},{v}) not in graph"

    # Property 4: the reported edges chain into a closed loop.
    # Determine the traversed (tail, head) for each edge accounting for direction.
    def traversed_endpoints(edge):
        u, v = edge[0], edge[1]
        if has_direction and edge[-1] == 'reverse':
            return v, u
        return u, v

    endpoints = [traversed_endpoints(e) for e in result]
    # The chain must be connected head-to-tail and close back on itself.
    for i in range(len(endpoints)):
        _, head = endpoints[i]
        next_tail, _ = endpoints[(i + 1) % len(endpoints)]
        assert head == next_tail, (
            f"Cycle not properly chained: edge {result[i]} head {head} "
            f"does not match next tail {next_tail}"
        )
# End program