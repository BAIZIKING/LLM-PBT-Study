from hypothesis import given, strategies as st
import networkx as nx
import math

# Summary: Generate random DiGraphs with small integer nodes and finite positive
# capacities on edges (avoiding infinite-capacity unbounded paths). Pick distinct
# source and sink nodes from the graph. Then verify non-negativity of flow value,
# flow conservation at intermediate nodes, capacity constraints, and that the flow
# value equals the net outflow at the source and net inflow at the sink.
@given(st.data())
def test_networkx_maximum_flow(data):
    # Generate a set of nodes
    n_nodes = data.draw(st.integers(min_value=2, max_value=8), label="n_nodes")
    nodes = list(range(n_nodes))

    # Generate edges with finite positive capacities
    edges = data.draw(
        st.lists(
            st.tuples(
                st.sampled_from(nodes),
                st.sampled_from(nodes),
                st.floats(min_value=0.1, max_value=100.0,
                          allow_nan=False, allow_infinity=False),
            ),
            min_size=0,
            max_size=20,
        ),
        label="edges",
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for u, v, cap in edges:
        if u == v:
            continue  # skip self-loops to keep things clean
        G.add_edge(u, v, capacity=cap)

    # Choose distinct source and sink
    s = data.draw(st.sampled_from(nodes), label="source")
    t = data.draw(st.sampled_from([n for n in nodes if n != s]), label="sink")

    flow_value, flow_dict = nx.maximum_flow(G, s, t)

    tol = 1e-6

    # Property 1: flow value is non-negative
    assert flow_value >= -tol, f"Flow value should be non-negative, got {flow_value}"

    # Property 5: every edge in the graph appears in flow_dict
    for u, v in G.edges():
        assert u in flow_dict, f"Node {u} missing from flow_dict"
        assert v in flow_dict[u], f"Edge ({u},{v}) missing from flow_dict"

    # Property 3: capacity constraints and non-negativity of edge flows
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            assert f >= -tol, f"Flow on edge ({u},{v}) is negative: {f}"
            cap = G[u][v].get("capacity", math.inf)
            assert f <= cap + tol, (
                f"Flow {f} on edge ({u},{v}) exceeds capacity {cap}"
            )

    # Helper: net outflow at a node = sum(out_flow) - sum(in_flow)
    def net_outflow(node):
        out_f = sum(flow_dict.get(node, {}).values())
        in_f = sum(
            flow_dict.get(u, {}).get(node, 0.0) for u in flow_dict
        )
        return out_f - in_f

    # Property 2: flow conservation at intermediate nodes
    for node in nodes:
        if node == s or node == t:
            continue
        assert abs(net_outflow(node)) < 1e-4, (
            f"Flow not conserved at node {node}: net outflow = {net_outflow(node)}"
        )

    # Property 4: flow value equals net outflow at source and net inflow at sink
    assert abs(net_outflow(s) - flow_value) < 1e-4, (
        f"Net outflow at source {net_outflow(s)} != flow value {flow_value}"
    )
    assert abs((-net_outflow(t)) - flow_value) < 1e-4, (
        f"Net inflow at sink {-net_outflow(t)} != flow value {flow_value}"
    )
# End program