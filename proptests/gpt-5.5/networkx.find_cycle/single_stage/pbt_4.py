from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate small random Graph/DiGraph/MultiGraph/MultiDiGraph instances, including empty graphs, isolated nodes, self-loops, duplicate/multiedges, varied valid sources, and all orientation options; check that returned cycles are real closed walks using existing edges, or that NetworkXNoCycle is the documented failure mode.
@given(st.data())
def test_networkx_find_cycle(data):
    def has_undirected_multicycle(H):
        parent = {node: node for node in H.nodes}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            parent[ry] = rx
            return True

        edge_iter = H.edges(keys=True) if H.is_multigraph() else H.edges()
        for edge in edge_iter:
            u, v = edge[:2]
            if find(u) == find(v):
                return True
            union(u, v)
        return False

    def has_cycle_when_source_is_none(H, orientation):
        if H.is_directed() and orientation in (None, "original", "reverse"):
            return not nx.is_directed_acyclic_graph(H)
        return has_undirected_multicycle(H)

    graph_cls = data.draw(
        st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]),
        label="graph_cls",
    )

    node_count = data.draw(st.integers(min_value=0, max_value=6), label="node_count")
    nodes = list(range(node_count))

    G = graph_cls()
    G.add_nodes_from(nodes)

    if nodes:
        edges = data.draw(
            st.lists(
                st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)),
                min_size=0,
                max_size=20,
            ),
            label="edges",
        )
        G.add_edges_from(edges)

        source = data.draw(
            st.one_of(
                st.none(),
                st.sampled_from(nodes),
                st.lists(st.sampled_from(nodes), min_size=1, max_size=8),
            ),
            label="source",
        )
    else:
        source = None

    orientation = data.draw(
        st.sampled_from([None, "original", "reverse", "ignore"]),
        label="orientation",
    )

    try:
        cycle = list(nx.find_cycle(G, source=source, orientation=orientation))
    except nx.NetworkXNoCycle:
        # When searching the whole graph, independently check the documented
        # meaning of NetworkXNoCycle for the chosen orientation.
        if source is None:
            assert not has_cycle_when_source_is_none(G, orientation)
        return

    # If a cycle is returned, it must be non-empty and every tuple must describe
    # an edge that actually exists in G.
    assert cycle

    traversed_edges = []
    for edge in cycle:
        assert isinstance(edge, tuple)

        if edge[-1] in ("forward", "reverse"):
            direction = edge[-1]
            core = edge[:-1]
            assert orientation is not None
        else:
            direction = None
            core = edge

        if G.is_multigraph():
            assert len(core) == 3
            u, v, key = core
            assert G.has_edge(u, v, key)
        else:
            assert len(core) == 2
            u, v = core
            assert G.has_edge(u, v)

        # Convert the reported edge into the direction actually traversed.
        if direction == "reverse":
            tail, head = v, u
        else:
            tail, head = u, v

        traversed_edges.append((tail, head))

    # The returned edges must form one closed cyclic walk.
    for (_, previous_head), (next_tail, _) in zip(
        traversed_edges, traversed_edges[1:]
    ):
        assert previous_head == next_tail

    assert traversed_edges[-1][1] == traversed_edges[0][0]
# End program