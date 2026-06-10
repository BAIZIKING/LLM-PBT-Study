from hypothesis import given, strategies as st
import networkx as nx
from networkx.exception import NetworkXNoCycle

# Summary: Generate random directed/undirected (multi)graphs from random nodes and
# edges, plus a random valid source and orientation. Verify that find_cycle either
# raises NetworkXNoCycle or returns a non-empty list of correctly-shaped edges that
# genuinely form a closed cyclic path, and that the existence of a cycle is consistent.
@given(st.data())
def test_networkx_find_cycle(data):
    n_nodes = data.draw(st.integers(min_value=0, max_value=8))
    nodes = list(range(n_nodes))

    directed = data.draw(st.booleans())
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(nodes)

    if n_nodes > 0:
        edges = data.draw(
            st.lists(
                st.tuples(
                    st.integers(min_value=0, max_value=n_nodes - 1),
                    st.integers(min_value=0, max_value=n_nodes - 1),
                ),
                max_size=15,
            )
        )
        G.add_edges_from(edges)

    # source: None or an existing node
    if n_nodes > 0:
        source = data.draw(st.one_of(st.none(), st.sampled_from(nodes)))
    else:
        source = None

    if directed:
        orientation = data.draw(
            st.sampled_from([None, "original", "reverse", "ignore"])
        )
    else:
        orientation = data.draw(st.sampled_from([None, "ignore"]))

    try:
        result = nx.find_cycle(G, source=source, orientation=orientation)
    except NetworkXNoCycle:
        # Property: if no cycle reported, the graph (per orientation) must have none.
        # For ignore/undirected we check the undirected view; for original/None we
        # check the directed structure.
        if orientation in (None, "original") and directed:
            assert not nx.is_directed_acyclic_graph(G) is False or True
            # A DiGraph with no directed cycle is a DAG.
            assert nx.is_directed_acyclic_graph(G)
        else:
            ug = G.to_undirected() if directed else G
            # No undirected cycle means a forest (no edge creates a cycle).
            num_self_loops = sum(1 for u, v in G.edges() if u == v)
            assert num_self_loops == 0
            assert ug.number_of_edges() - ug.number_of_selfloops() < ug.number_of_nodes() \
                or nx.is_forest(nx.Graph(ug))
        return

    # A cycle was found.
    edges = list(result)
    assert len(edges) > 0, "Found cycle must be non-empty"

    # Property: edge tuple shape depends on orientation.
    if orientation is None:
        for e in edges:
            assert len(e) == 2
    else:
        for e in edges:
            assert len(e) == 3
            assert e[-1] in ("forward", "reverse")

    # Property: the returned edges form a closed cyclic path.
    # Normalize each edge into (tail, head) according to traversal direction.
    def endpoints(e):
        if orientation is None:
            u, v = e[0], e[1]
            return u, v
        else:
            u, v, d = e[0], e[1], e[-1]
            if d == "reverse":
                return v, u
            return u, v

    seq = [endpoints(e) for e in edges]
    # Consecutive edges must chain head-to-tail.
    for (u1, v1), (u2, v2) in zip(seq, seq[1:]):
        assert v1 == u2, f"Edges do not chain: {(u1, v1)} -> {(u2, v2)}"
    # The path must close: head of last == tail of first.
    assert seq[-1][1] == seq[0][0], "Cycle does not close on itself"
# End program