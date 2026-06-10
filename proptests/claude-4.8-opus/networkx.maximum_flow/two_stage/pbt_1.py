from hypothesis import given, strategies as st, assume, settings
import networkx as nx
from networkx.algorithms.flow import (
    edmonds_karp,
    shortest_augmenting_path,
    preflow_push,
)


# Strategy that builds a DiGraph with capacities, plus a chosen source and sink.
@st.composite
def flow_graphs(draw):
    n = draw(st.integers(min_value=2, max_value=8))
    nodes = list(range(n))
    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    # Generate a set of possible directed edges (no self-loops).
    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    edges = draw(
        st.lists(
            st.sampled_from(possible_edges),
            unique=True,
            max_size=len(possible_edges),
        )
    )
    for (u, v) in edges:
        cap = draw(
            st.floats(
                min_value=0.0,
                max_value=1000.0,
                allow_nan=False,
                allow_infinity=False,
            )
        )
        G.add_edge(u, v, capacity=cap)

    s = draw(st.sampled_from(nodes))
    t = draw(st.sampled_from([x for x in nodes if x != s]))
    return G, s, t


@settings(deadline=None)
@given(st.data())
def test_networkx_maximum_flow_property():
    G, s, t = st.data().example() if False else None, None, None  # placeholder

    # Properly draw the data inside the test.
    # (We use the data() fixture below.)


@settings(deadline=None)
@given(data=st.data())
def test_networkx_maximum_flow_properties(data):
    G, s, t = data.draw(flow_graphs())

    flow_value, flow_dict = nx.maximum_flow(G, s, t)

    tol = 1e-6

    # ---- Property 4 (part): flow_value is non-negative ----
    assert flow_value >= -tol

    # Helper: outflow and inflow at a node from flow_dict.
    def outflow(node):
        return sum(flow_dict.get(node, {}).values())

    def inflow(node):
        total = 0.0
        for u in flow_dict:
            for v, f in flow_dict[u].items():
                if v == node:
                    total += f
        return total

    # ---- Property 1: net outflow from source == net inflow into sink == flow_value ----
    net_source = outflow(s) - inflow(s)
    net_sink = inflow(t) - outflow(t)
    assert abs(net_source - flow_value) <= tol + tol * abs(flow_value)
    assert abs(net_sink - flow_value) <= tol + tol * abs(flow_value)

    # ---- Property 4 (part): flow_value == sum of flows out of source ----
    # Since flows are non-negative and there are typically no edges into the
    # source under a max-flow assignment, net_source equals flow_value (checked
    # above). We also assert flow_value equals net outflow from source.
    assert abs(net_source - flow_value) <= tol + tol * abs(flow_value)

    # ---- Property 2: flow conservation at intermediate nodes ----
    for node in G.nodes():
        if node == s or node == t:
            continue
        assert abs(inflow(node) - outflow(node)) <= tol + tol * max(
            abs(inflow(node)), abs(outflow(node)), 1.0
        )

    # ---- Property 3: capacity constraints and non-negativity ----
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            assert f >= -tol, f"negative flow on edge ({u},{v}): {f}"
            if G.has_edge(u, v) and "capacity" in G[u][v]:
                cap = G[u][v]["capacity"]
                assert f <= cap + tol + tol * abs(cap), (
                    f"flow {f} exceeds capacity {cap} on edge ({u},{v})"
                )

    # ---- Property 5: invariance of flow_value across algorithms ----
    for flow_func in (edmonds_karp, shortest_augmenting_path, preflow_push):
        fv = nx.maximum_flow(G, s, t, flow_func=flow_func)[0]
        assert abs(fv - flow_value) <= tol + tol * abs(flow_value), (
            f"{flow_func.__name__} gave {fv}, expected {flow_value}"
        )
# End program