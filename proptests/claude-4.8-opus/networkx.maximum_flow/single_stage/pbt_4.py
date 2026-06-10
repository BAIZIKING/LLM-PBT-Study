from hypothesis import given, strategies as st, settings
import networkx as nx
import math

# Summary: Generate a random nx.DiGraph with a small number of nodes, random edges
# (no self-loops) with finite positive capacities to avoid NetworkXUnbounded, and
# pick two distinct nodes as source and sink. Then verify maximum_flow's output
# satisfies non-negativity, capacity constraints, flow conservation at intermediate
# nodes, source/sink net flow equals flow_value, and consistency with
# maximum_flow_value.
@given(st.data())
@settings(max_examples=300, deadline=None)
def test_networkx_maximum_flow(data):
    # Generate number of nodes (need at least 2 for distinct s and t)
    n = data.draw(st.integers(min_value=2, max_value=8), label="num_nodes")
    nodes = list(range(n))

    # Generate a set of directed edges (no self-loops)
    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    chosen = data.draw(
        st.lists(st.sampled_from(possible_edges), unique=True, max_size=len(possible_edges)),
        label="edges",
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for (u, v) in chosen:
        cap = data.draw(
            st.one_of(
                st.integers(min_value=0, max_value=20),
                st.floats(min_value=0.0, max_value=20.0,
                          allow_nan=False, allow_infinity=False),
            ),
            label=f"cap_{u}_{v}",
        )
        G.add_edge(u, v, capacity=cap)

    # Pick distinct source and sink
    s = data.draw(st.sampled_from(nodes), label="source")
    t = data.draw(st.sampled_from([x for x in nodes if x != s]), label="sink")

    flow_value, flow_dict = nx.maximum_flow(G, s, t)

    TOL = 1e-6

    # Property 1: flow value is non-negative
    assert flow_value >= -TOL, f"Flow value negative: {flow_value}"

    # Property 2: capacity constraints on each edge
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            assert f >= -TOL, f"Negative flow on edge ({u},{v}): {f}"
            cap = G[u][v].get("capacity")
            if cap is not None:
                assert f <= cap + TOL, (
                    f"Flow {f} exceeds capacity {cap} on edge ({u},{v})"
                )

    # Helper: compute net outflow (out - in) for a node from flow_dict
    def net_outflow(node):
        out_flow = sum(flow_dict.get(node, {}).values())
        in_flow = sum(
            flow_dict.get(u, {}).get(node, 0.0) for u in flow_dict
        )
        return out_flow - in_flow

    # Property 3: net outflow from source equals flow_value
    assert math.isclose(net_outflow(s), flow_value, rel_tol=1e-6, abs_tol=TOL), (
        f"Net outflow from source {net_outflow(s)} != flow_value {flow_value}"
    )

    # Property 4: net inflow into sink equals flow_value
    assert math.isclose(-net_outflow(t), flow_value, rel_tol=1e-6, abs_tol=TOL), (
        f"Net inflow into sink {-net_outflow(t)} != flow_value {flow_value}"
    )

    # Property 5: flow conservation at every intermediate node
    for node in nodes:
        if node == s or node == t:
            continue
        assert math.isclose(net_outflow(node), 0.0, rel_tol=1e-6, abs_tol=TOL), (
            f"Flow not conserved at node {node}: net outflow {net_outflow(node)}"
        )

    # Property 6: consistency with maximum_flow_value
    fv_only = nx.maximum_flow_value(G, s, t)
    assert math.isclose(fv_only, flow_value, rel_tol=1e-6, abs_tol=TOL), (
        f"maximum_flow_value {fv_only} != maximum_flow value {flow_value}"
    )
# End program