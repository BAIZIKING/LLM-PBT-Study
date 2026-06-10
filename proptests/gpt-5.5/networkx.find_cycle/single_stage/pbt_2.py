from hypothesis import given, strategies as st
import networkx as nx
from networkx.exception import NetworkXNoCycle

# Summary: Generate small random Graph/DiGraph/MultiGraph/MultiDiGraph inputs, random valid
# source values, and valid orientation values. Half the cases deliberately contain a reachable
# cycle; the other half are forests/DAG-like graphs with no directed or undirected cycles. Check
# that find_cycle raises NetworkXNoCycle exactly for the no-cycle construction, and otherwise
# returns a non-empty closed edge path whose edge tuple shapes, edge existence, and traversal
# directions match the API documentation.
@given(st.data())
def test_networkx_find_cycle(data):
    is_directed = data.draw(st.booleans())
    is_multigraph = data.draw(st.booleans())

    graph_type = {
        (False, False): nx.Graph,
        (True, False): nx.DiGraph,
        (False, True): nx.MultiGraph,
        (True, True): nx.MultiDiGraph,
    }[(is_directed, is_multigraph)]

    G = graph_type()
    n = data.draw(st.integers(min_value=1, max_value=6))
    nodes = list(range(n))
    G.add_nodes_from(nodes)

    if is_directed:
        orientation = data.draw(st.sampled_from([None, "original", "reverse", "ignore"]))
    else:
        # The orientation parameter is documented as controlling directed graphs.
        orientation = None

    has_reachable_cycle = data.draw(st.booleans())
    cycle_nodes = []

    if has_reachable_cycle:
        if n >= 3:
            cycle_len = data.draw(st.one_of(st.just(1), st.integers(min_value=3, max_value=n)))
        else:
            cycle_len = 1

        cycle_nodes = data.draw(
            st.lists(
                st.sampled_from(nodes),
                min_size=cycle_len,
                max_size=cycle_len,
                unique=True,
            )
        )

        if cycle_len == 1:
            G.add_edge(cycle_nodes[0], cycle_nodes[0])
        else:
            for u, v in zip(cycle_nodes, cycle_nodes[1:] + cycle_nodes[:1]):
                G.add_edge(u, v)

        extra_edges = data.draw(
            st.lists(
                st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)),
                min_size=0,
                max_size=12,
            )
        )
        for u, v in extra_edges:
            G.add_edge(u, v)

        anchor = cycle_nodes[0]
        source_kind = data.draw(st.sampled_from(["none", "node", "list"]))
        if source_kind == "none":
            source = None
        elif source_kind == "node":
            source = anchor
        else:
            extra_sources = data.draw(
                st.lists(st.sampled_from(nodes), min_size=0, max_size=n, unique=True)
            )
            source = [anchor] + [u for u in extra_sources if u != anchor]

    else:
        # Build an underlying forest. For directed graphs, orient each forest edge randomly;
        # this remains acyclic under "original", "reverse", and "ignore".
        for child in range(1, n):
            if data.draw(st.booleans()):
                parent = data.draw(st.integers(min_value=0, max_value=child - 1))
                if is_directed and data.draw(st.booleans()):
                    G.add_edge(child, parent)
                else:
                    G.add_edge(parent, child)

        source_kind = data.draw(st.sampled_from(["none", "node", "list", "empty_list"]))
        if source_kind == "none":
            source = None
        elif source_kind == "node":
            source = data.draw(st.sampled_from(nodes))
        elif source_kind == "empty_list":
            source = []
        else:
            source = data.draw(
                st.lists(st.sampled_from(nodes), min_size=0, max_size=n, unique=True)
            )

    try:
        cycle = nx.find_cycle(G, source=source, orientation=orientation)
    except NetworkXNoCycle:
        assert not has_reachable_cycle
        return

    assert has_reachable_cycle
    assert isinstance(cycle, list)
    assert len(cycle) >= 1

    traversed = []

    for edge in cycle:
        if is_multigraph:
            if is_directed and orientation is not None:
                assert len(edge) == 4
                u, v, key, direction = edge
            else:
                assert len(edge) == 3
                u, v, key = edge
                direction = None
            assert G.has_edge(u, v, key)
        else:
            if is_directed and orientation is not None:
                assert len(edge) == 3
                u, v, direction = edge
            else:
                assert len(edge) == 2
                u, v = edge
                direction = None
            assert G.has_edge(u, v)

        if is_directed and orientation is not None:
            assert direction in {"forward", "reverse"}
            if direction == "reverse":
                tail, head = v, u
            else:
                tail, head = u, v
        else:
            tail, head = u, v

        traversed.append((tail, head))

    for (_, head), (next_tail, _) in zip(traversed, traversed[1:]):
        assert head == next_tail

    assert traversed[-1][1] == traversed[0][0]
# End program