from hypothesis import given, strategies as st, settings, assume
import networkx as nx
from networkx.algorithms.flow import (
    edmonds_karp,
    shortest_augmenting_path,
    preflow_push,
    dinitz,
    boykov_kolmogorov,
)


# Strategy to build a capacitated DiGraph with a designated source and sink.
@st.composite
def flow_graphs(draw):
    # Number of nodes between 2 and 8
    n = draw(st.integers(min_value=2, max_value=8))
    nodes = list(range(n))

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    # Generate edges with finite, bounded, non-negative capacities to avoid
    # overflow and unbounded flow.
    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    # Decide for each possible edge whether it exists.
    for (u, v) in possible_edges:
        if draw(st.booleans()):
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
    t = draw(st.sampled_from(nodes))
    assume(s != t)

    return G, s, t


def _out_flow(flow_dict, node):
    return sum(flow_dict.get(node, {}).values())


def _in_flow(flow_dict, node, G):
    total = 0.0
    for u in G.nodes():
        nbrs = flow_dict.get(u, {})
        if node in nbrs:
            total += nbrs[node]
    return total


TOL = 1e-4


@given(flow_graphs())
@settings(max_examples=300)
def test_networkx_maximum_flow_property(data):
    G, s, t = data

    flow_value, flow_dict = nx.maximum_flow(G, s, t)

    # Property 1: flow value equals net outflow from the source.
    net_out_source = _out_flow(flow_dict, s) - _in_flow(flow_dict, s, G)
    assert abs(flow_value - net_out_source) <= TOL * max(1.0, abs(flow_value))

    # Property 2: flow value equals net inflow into the sink.
    net_in_sink = _in_flow(flow_dict, t, G) - _out_flow(flow_dict, t)
    assert abs(flow_value - net_in_sink) <= TOL * max(1.0, abs(flow_value))

    # Property 3: flow conservation at every non-source, non-sink node.
    for node in G.nodes():
        if node == s or node == t:
            continue
        inflow = _in_flow(flow_dict, node, G)
        outflow = _out_flow(flow_dict, node)
        assert abs(inflow - outflow) <= TOL * max(1.0, abs(inflow), abs(outflow))

    # Property 4: each edge flow is non-negative and within capacity.
    for u in flow_dict:
        for v, f in flow_dict[u].items():
            assert f >= -TOL
            cap = G[u][v].get("capacity", float("inf"))
            assert f <= cap + TOL * max(1.0, abs(cap))

    # Property 5: flow value non-negative and consistent across algorithms.
    assert flow_value >= -TOL

    for flow_func in (
        edmonds_karp,
        shortest_augmenting_path,
        preflow_push,
        dinitz,
        boykov_kolmogorov,
    ):
        alt_value, _ = nx.maximum_flow(G, s, t, flow_func=flow_func)
        assert abs(alt_value - flow_value) <= TOL * max(1.0, abs(flow_value))
# End program