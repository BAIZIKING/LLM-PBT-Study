from hypothesis import given, strategies as st
import networkx as nx
import math

# Summary: Generate random DiGraphs with a bounded number of nodes and random
# directed edges, each assigned a finite non-negative capacity (to avoid
# unbounded flow). Pick source and sink from existing nodes (allowing equal,
# disconnected, or distinct cases). Verify return types, non-negativity,
# flow conservation at intermediate nodes, net source outflow == net sink
# inflow == flow_value, and capacity constraints on every edge.
@given(st.data())
def test_networkx_maximum_flow(data):
    # --- Generate the graph ---
    n_nodes = data.draw(st.integers(min_value=1, max_value=8), label="n_nodes")
    nodes = list(range(n_nodes))

    # Generate a set of directed edges (no self-loops for simplicity of conservation checks)
    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    edges = data.draw(
        st.lists(st.sampled_from(possible_edges) if possible_edges else st.nothing(),
                 unique=True, max_size=len(possible_edges)),
        label="edges",
    ) if possible_edges else []

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for (u, v) in edges:
        # Always assign a finite non-negative capacity to avoid NetworkXUnbounded
        cap = data.draw(
            st.floats(min_value=0.0, max_value=1000.0,
                      allow_nan=False, allow_infinity=False),
            label=f"cap_{u}_{v}",
        )
        G.add_edge(u, v, capacity=cap)

    # --- Pick source and sink ---
    s = data.draw(st.sampled_from(nodes), label="source")
    t = data.draw(st.sampled_from(nodes), label="sink")

    flow_value, flow_dict = nx.maximum_flow(G, s, t)

    # Property 1: return types
    assert isinstance(flow_value, (int, float))
    assert isinstance(flow_dict, dict)

    # Property 2: non-negative flow value
    assert flow_value >= -1e-9

    TOL = 1e-6

    # Property 6 & 7: capacity constraints and flow on existing edges
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            assert G.has_edge(u, v), f"Flow on non-existent edge ({u},{v})"
            cap = G[u][v].get("capacity", math.inf)
            # flow must be non-negative and within capacity
            assert f >= -TOL, f"Negative flow on edge ({u},{v}): {f}"
            assert f <= cap + TOL, f"Flow {f} exceeds capacity {cap} on ({u},{v})"

    # Helper: compute net outflow at a node = sum(out) - sum(in)
    def net_outflow(node):
        out_sum = sum(flow_dict.get(node, {}).values())
        in_sum = 0.0
        for u in flow_dict:
            if node in flow_dict[u]:
                in_sum += flow_dict[u][node]
        return out_sum - in_sum

    if s == t:
        # Degenerate case: source equals sink; flow value should be 0
        assert abs(flow_value) <= TOL
    else:
        # Property 4: net outflow from source equals flow value
        assert abs(net_outflow(s) - flow_value) <= TOL, \
            f"Source net outflow {net_outflow(s)} != flow_value {flow_value}"

        # Property 5: net inflow to sink equals flow value
        assert abs((-net_outflow(t)) - flow_value) <= TOL, \
            f"Sink net inflow {-net_outflow(t)} != flow_value {flow_value}"

        # Property 3: flow conservation at all intermediate nodes
        for node in nodes:
            if node != s and node != t:
                assert abs(net_outflow(node)) <= TOL, \
                    f"Conservation violated at node {node}: net={net_outflow(node)}"
# End program