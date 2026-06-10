from hypothesis import given, settings, strategies as st
import networkx as nx
import math

# Summary: Build random DiGraphs with finite non-negative edge capacities (to
# avoid unbounded flow), pick a distinct source/sink, then verify max-flow
# invariants: return shape, non-negativity/finiteness, capacity constraints,
# flow conservation at internal nodes, flow-value == net source outflow ==
# net sink inflow, and the max-flow min-cut theorem.
@given(st.data())
@settings(max_examples=200, deadline=None)
def test_networkx_maximum_flow(data):
    # --- Generate nodes ---
    n_nodes = data.draw(st.integers(min_value=2, max_value=8), label="n_nodes")
    nodes = list(range(n_nodes))

    # --- Generate edges (distinct, no self-loops) with finite capacities ---
    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    chosen_edges = data.draw(
        st.lists(st.sampled_from(possible_edges), unique=True, max_size=len(possible_edges)),
        label="edges",
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for (u, v) in chosen_edges:
        cap = data.draw(
            st.one_of(
                st.integers(min_value=0, max_value=20),
                st.floats(min_value=0.0, max_value=20.0,
                          allow_nan=False, allow_infinity=False),
            ),
            label=f"cap_{u}_{v}",
        )
        G.add_edge(u, v, capacity=float(cap))

    # --- Pick distinct source and sink ---
    s = data.draw(st.sampled_from(nodes), label="source")
    t = data.draw(st.sampled_from([x for x in nodes if x != s]), label="sink")

    # --- Run the function under test ---
    flow_value, flow_dict = nx.maximum_flow(G, s, t)

    # Property 1: return shape
    assert isinstance(flow_dict, dict)
    assert isinstance(flow_value, (int, float))

    # Property 2: non-negativity and finiteness
    assert flow_value >= -1e-9
    assert math.isfinite(flow_value)

    tol = 1e-6

    # Property 3: capacity constraints (0 <= flow <= capacity)
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            assert f >= -tol, f"negative flow on edge ({u},{v}): {f}"
            cap = G[u][v]["capacity"]
            assert f <= cap + tol, f"flow {f} exceeds capacity {cap} on ({u},{v})"

    # Property 4 & 5: flow conservation + flow value consistency
    def outflow(node):
        return sum(flow_dict.get(node, {}).values())

    def inflow(node):
        total = 0.0
        for u in flow_dict:
            total += flow_dict[u].get(node, 0.0)
        return total

    for node in nodes:
        if node == s or node == t:
            continue
        net = outflow(node) - inflow(node)
        assert abs(net) <= tol, f"flow not conserved at node {node}: net={net}"

    # net outflow from source == flow_value
    net_source = outflow(s) - inflow(s)
    assert abs(net_source - flow_value) <= tol, (
        f"source net outflow {net_source} != flow_value {flow_value}"
    )
    # net inflow to sink == flow_value
    net_sink = inflow(t) - outflow(t)
    assert abs(net_sink - flow_value) <= tol, (
        f"sink net inflow {net_sink} != flow_value {flow_value}"
    )

    # Property 6: max-flow min-cut theorem
    cut_value = nx.minimum_cut_value(G, s, t)
    assert abs(flow_value - cut_value) <= tol, (
        f"max-flow {flow_value} != min-cut {cut_value}"
    )

    # Property 7: consistency with maximum_flow_value()
    value_only = nx.maximum_flow_value(G, s, t)
    assert abs(flow_value - value_only) <= tol, (
        f"maximum_flow value {flow_value} != maximum_flow_value {value_only}"
    )
# End program