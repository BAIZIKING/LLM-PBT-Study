from hypothesis import given, strategies as st
import networkx as nx
from networkx.exception import NetworkXNoCycle

# Summary: Generate Graph/DiGraph/MultiGraph/MultiDiGraph instances with 0-7 integer nodes,
# random edges including self-loops and duplicate parallel edges, random valid sources
# including None, a single existing node, or a nonempty list of existing nodes, and every
# documented orientation value. If find_cycle returns, verify that the returned edge list
# is a closed cyclic traversal using real graph edges and correct orientation metadata.
# If NetworkXNoCycle is raised, independently check that no reachable directed/undirected
# cycle exists under the requested traversal semantics.
@given(st.data())
def test_networkx_find_cycle(data):
    graph_cls = data.draw(
        st.sampled_from([nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]),
        label="graph_cls",
    )
    G = graph_cls()

    n = data.draw(st.integers(min_value=0, max_value=7), label="node_count")
    nodes = list(range(n))
    G.add_nodes_from(nodes)

    if nodes:
        edge_count = data.draw(st.integers(min_value=0, max_value=18), label="edge_count")
        edge_strategy = st.tuples(st.sampled_from(nodes), st.sampled_from(nodes))
        edges = data.draw(st.lists(edge_strategy, min_size=edge_count, max_size=edge_count), label="edges")
        G.add_edges_from(edges)

        source = data.draw(
            st.one_of(
                st.none(),
                st.sampled_from(nodes),
                st.lists(
                    st.sampled_from(nodes),
                    min_size=1,
                    max_size=min(4, len(nodes)),
                    unique=True,
                ),
            ),
            label="source",
        )
    else:
        source = None

    orientation = data.draw(
        st.sampled_from([None, "original", "reverse", "ignore"]),
        label="orientation",
    )

    def source_nodes():
        if source is None:
            return list(G.nodes)
        if isinstance(source, list):
            return source
        return [source]

    def reachable_directed_nodes(reverse=False):
        starts = source_nodes()
        if source is None:
            return set(G.nodes)

        adjacency = {u: set() for u in G.nodes}
        for u, v in G.edges():
            if reverse:
                adjacency[v].add(u)
            else:
                adjacency[u].add(v)

        seen = set()
        stack = list(starts)
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            stack.extend(adjacency.get(u, ()) - seen)
        return seen

    def reachable_undirected_nodes():
        if source is None:
            return set(G.nodes)

        starts = source_nodes()
        adjacency = {u: set() for u in G.nodes}
        for u, v in G.edges():
            adjacency[u].add(v)
            adjacency[v].add(u)

        seen = set()
        stack = list(starts)
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            stack.extend(adjacency.get(u, ()) - seen)
        return seen

    def has_directed_cycle(reverse=False):
        reachable = reachable_directed_nodes(reverse=reverse)
        adjacency = {u: set() for u in reachable}

        for u, v in G.edges():
            a, b = (v, u) if reverse else (u, v)
            if a in reachable and b in reachable:
                adjacency[a].add(b)

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {u: WHITE for u in reachable}

        def dfs(u):
            color[u] = GRAY
            for v in adjacency[u]:
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            return False

        return any(color[u] == WHITE and dfs(u) for u in reachable)

    def has_undirected_cycle():
        reachable = reachable_undirected_nodes()

        # A self-loop is a cycle.
        for u, v in G.edges():
            if u == v and u in reachable:
                return True

        # Parallel edges between the same two reachable nodes form a 2-cycle in a multigraph.
        if G.is_multigraph():
            pair_counts = {}
            for u, v, _key in G.edges(keys=True):
                if u in reachable and v in reachable and u != v:
                    pair = frozenset((u, v))
                    pair_counts[pair] = pair_counts.get(pair, 0) + 1
                    if pair_counts[pair] >= 2:
                        return True

        # Otherwise, check for an ordinary undirected simple cycle.
        parent = {}

        adjacency = {u: set() for u in reachable}
        for u, v in G.edges():
            if u in reachable and v in reachable and u != v:
                adjacency[u].add(v)
                adjacency[v].add(u)

        def dfs(u, p):
            parent[u] = p
            for v in adjacency[u]:
                if v == p:
                    continue
                if v in parent:
                    return True
                if dfs(v, u):
                    return True
            return False

        return any(u not in parent and dfs(u, None) for u in reachable)

    def expected_cycle_exists():
        if G.is_directed() and orientation not in ("ignore",):
            return has_directed_cycle(reverse=(orientation == "reverse"))
        return has_undirected_cycle()

    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
    except NetworkXNoCycle:
        assert not expected_cycle_exists()
        return

    assert isinstance(cycle, list)
    assert len(cycle) > 0

    traversal = []
    for edge in cycle:
        assert isinstance(edge, tuple)

        has_direction_marker = edge[-1] in ("forward", "reverse")
        if G.is_directed() and orientation is not None:
            assert has_direction_marker
        if orientation is None:
            assert not has_direction_marker

        direction = edge[-1] if has_direction_marker else None
        core = edge[:-1] if has_direction_marker else edge

        if G.is_multigraph():
            assert len(core) == 3
            u, v, key = core
            assert G.has_edge(u, v, key)
        else:
            assert len(core) == 2
            u, v = core
            assert G.has_edge(u, v)

        if G.is_directed():
            if direction == "reverse":
                traversal.append((v, u))
            else:
                traversal.append((u, v))
        else:
            traversal.append((u, v))

    for (_, head), (next_tail, _) in zip(traversal, traversal[1:] + traversal[:1]):
        assert head == next_tail
# End program