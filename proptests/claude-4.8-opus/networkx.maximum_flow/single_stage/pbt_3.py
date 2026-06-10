from hypothesis import given, strategies as st
import networkx as nx
import math

# Summary: Generate random DiGraphs with finite positive capacities (to avoid
# NetworkXUnbounded), pick distinct source/sink nodes, then verify non-negativity,
# flow conservation, capacity constraints, flow-value consistency, and agreement
# with maximum_flow_value.
@given(st.data())
def test_networkx_maximum_flow(data):
    # Number of nodes: at least 2 so we can pick distinct source and sink.
    num_nodes = data.draw(st.integers(min_value=2, max_value=8), label="num_nodes")
    nodes = list(range(num_nodes))

    # Generate a set of directed edges with finite positive capacities.
    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    edges = data.draw(
        st.lists(
            st.sampled_from(possible_edges) if possible_edges else st.nothing(),
            unique=True,
            max_size=len(possible_edges),
        ),
        label="edges",
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for (u, v) in edges:
        capacity = data.draw(
            st.floats(min_value=0.0, max_value=1000.0,
                      allow_nan=False, allow_infinity=False),
            label=f"cap_{u}_{v}",
        )
        G.add_edge(u, v, capacity=capacity)

    # Pick distinct source and sink.
    s = data.draw(st.sampled_from(nodes), label="source")
    t = data.draw(st.sampled_from([n for n in nodes if n != s]), label="sink")

    flow_value, flow_dict = nx.maximum_flow(G, s, t)

    tol = 1e-6

    # Property 1: Non-negativity of the maximum flow value.
    assert flow_value >= -tol

    # Property 2 & 3: Capacity constraints and non-negative flows on edges.
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            assert f >= -tol, f"Negative flow on edge ({u},{v}): {f}"
            cap = G[u][v]["capacity"]
            assert f <= cap + tol, (
                f"Flow {f} exceeds capacity {cap} on edge ({u},{v})"
            )

    # Helper to compute total outflow and inflow for a node.
    def out_flow(node):
        return sum(flow_dict.get(node, {}).values())

    def in_flow(node):
        total = 0.0
        for u in flow_dict:
            total += flow_dict[u].get(node, 0.0)
        return total

    # Property 4: Flow conservation for intermediate nodes.
    for node in nodes:
        if node == s or node == t:
            continue
        assert math.isclose(out_flow(node), in_flow(node), abs_tol=1e-5), (
            f"Conservation violated at node {node}: "
            f"out={out_flow(node)} in={in_flow(node)}"
        )

    # Property 5: flow_value equals net outflow from source and net inflow to sink.
    net_source = out_flow(s) - in_flow(s)
    net_sink = in_flow(t) - out_flow(t)
    assert math.isclose(flow_value, net_source, abs_tol=1e-5)
    assert math.isclose(flow_value, net_sink, abs_tol=1e-5)

    # Property 6: Consistency with maximum_flow_value.
    mf_value = nx.maximum_flow_value(G, s, t)
    assert math.isclose(flow_value, mf_value, abs_tol=1e-5)
# End program