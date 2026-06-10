from hypothesis import given, strategies as st
import networkx

@given(st.data())
def test_networkx_find_cycle_property(data):
    graph_kind = data.draw(
        st.sampled_from(["graph", "digraph", "multigraph", "multidigraph"])
    )

    if graph_kind == "graph":
        G = networkx.Graph()
    elif graph_kind == "digraph":
        G = networkx.DiGraph()
    elif graph_kind == "multigraph":
        G = networkx.MultiGraph()
    else:
        G = networkx.MultiDiGraph()

    is_directed = G.is_directed()
    is_multigraph = G.is_multigraph()

    if is_directed:
        orientation = data.draw(st.sampled_from([None, "original", "reverse", "ignore"]))
    else:
        orientation = None

    node_count = data.draw(st.integers(min_value=0, max_value=6))
    nodes = list(range(node_count))
    G.add_nodes_from(nodes)

    if node_count > 0:
        random_edges = data.draw(
            st.lists(
                st.tuples(
                    st.integers(min_value=0, max_value=node_count - 1),
                    st.integers(min_value=0, max_value=node_count - 1),
                ),
                min_size=0,
                max_size=14,
            )
        )
    else:
        random_edges = []

    if is_multigraph:
        for key, (u, v) in enumerate(random_edges):
            G.add_edge(u, v, key=("random", key))
    else:
        G.add_edges_from(random_edges)

    if node_count > 0 and data.draw(st.booleans()):
        if not is_directed and not is_multigraph:
            possible_cycle_lengths = [1] + list(range(3, node_count + 1))
            cycle_length = data.draw(st.sampled_from(possible_cycle_lengths))
        else:
            cycle_length = data.draw(st.integers(min_value=1, max_value=node_count))

        cycle_nodes = data.draw(
            st.lists(
                st.sampled_from(nodes),
                min_size=cycle_length,
                max_size=cycle_length,
                unique=True,
            )
        )

        for i in range(cycle_length):
            u = cycle_nodes[i]
            v = cycle_nodes[(i + 1) % cycle_length]
            if is_multigraph:
                G.add_edge(u, v, key=("cycle", i))
            else:
                G.add_edge(u, v)

    try:
        cycle = networkx.find_cycle(G, orientation=orientation)
    except networkx.exception.NetworkXNoCycle:
        return

    assert isinstance(cycle, list)
    assert len(cycle) > 0

    expected_edge_length = 3 if is_multigraph else 2
    if orientation is not None:
        expected_edge_length += 1

    traversal_edges = []

    for edge in cycle:
        assert isinstance(edge, tuple)
        assert len(edge) == expected_edge_length

        u = edge[0]
        v = edge[1]

        if is_multigraph:
            key = edge[2]
            assert G.has_edge(u, v, key)
        else:
            assert G.has_edge(u, v)

        if orientation is None:
            traversal_tail, traversal_head = u, v
        else:
            direction = edge[-1]
            assert direction in {"forward", "reverse"}

            if orientation == "original":
                assert direction == "forward"
            elif orientation == "reverse":
                assert direction == "reverse"

            if direction == "forward":
                traversal_tail, traversal_head = u, v
            else:
                traversal_tail, traversal_head = v, u

        traversal_edges.append((traversal_tail, traversal_head))

    for i in range(len(traversal_edges)):
        current_head = traversal_edges[i][1]
        next_tail = traversal_edges[(i + 1) % len(traversal_edges)][0]
        assert current_head == next_tail
# End program