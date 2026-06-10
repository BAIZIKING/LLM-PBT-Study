from hypothesis import given, strategies as st
import math
import networkx as nx
from networkx.algorithms.flow import edmonds_karp, shortest_augmenting_path
from networkx.exception import NetworkXError, NetworkXNotImplemented, NetworkXUnbounded

# Summary: Generate small random DiGraph/MultiDiGraph inputs with 2-7 nodes,
# random source/sink pairs, sparse-to-dense directed edge sets, custom capacity
# attribute names, finite integer/float capacities including zero, and missing
# capacity attributes representing infinite capacity. Also vary flow_func between
# the default and alternative documented algorithms. Properties checked:
# MultiDiGraph inputs raise the documented unsupported-graph error; graphs with
# an all-infinite-capacity s-t path raise NetworkXUnbounded; otherwise the
# returned flow respects capacities, conserves flow at intermediate nodes, has
# source/sink net flow equal to flow_value, and matches the minimum cut value.
@given(st.data())
def test_networkx_maximum_flow(data):
    n = data.draw(st.integers(min_value=2, max_value=7), label="node_count")
    nodes = list(range(n))

    source, sink = data.draw(
        st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)).filter(
            lambda pair: pair[0] != pair[1]
        ),
        label="source_sink",
    )

    graph_kind = data.draw(
        st.sampled_from(["digraph", "digraph", "digraph", "multidigraph"]),
        label="graph_kind",
    )
    G = nx.DiGraph() if graph_kind == "digraph" else nx.MultiDiGraph()
    G.add_nodes_from(nodes)

    capacity_key = data.draw(
        st.sampled_from(["capacity", "cap", "bandwidth"]),
        label="capacity_key",
    )

    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    edges = data.draw(
        st.lists(
            st.sampled_from(possible_edges),
            unique=True,
            min_size=0,
            max_size=len(possible_edges),
        ),
        label="edges",
    )

    finite_capacity = st.one_of(
        st.integers(min_value=0, max_value=20),
        st.floats(
            min_value=0,
            max_value=20,
            allow_nan=False,
            allow_infinity=False,
            width=16,
        ),
    )

    for u, v in edges:
        attrs = {}

        # None means the selected capacity attribute is absent, so NetworkX
        # treats this edge as having infinite capacity.
        cap = data.draw(st.one_of(st.none(), finite_capacity), label="edge_capacity")
        if cap is not None:
            attrs[capacity_key] = cap

        # Add occasional irrelevant capacity-looking data to ensure the chosen
        # `capacity` parameter, not necessarily the literal "capacity", is used.
        if capacity_key != "capacity":
            distractor = data.draw(st.one_of(st.none(), finite_capacity), label="distractor")
            if distractor is not None:
                attrs["capacity"] = distractor

        G.add_edge(u, v, **attrs)

    flow_func = data.draw(
        st.sampled_from([None, edmonds_karp, shortest_augmenting_path]),
        label="flow_func",
    )

    if graph_kind == "multidigraph":
        try:
            nx.maximum_flow(
                G,
                source,
                sink,
                capacity=capacity_key,
                flow_func=flow_func,
            )
            assert False, "maximum_flow should reject MultiDiGraph inputs"
        except (NetworkXError, NetworkXNotImplemented):
            return

    # A path using only edges missing the chosen capacity attribute has infinite
    # capacity, so the maximum feasible flow is unbounded.
    infinite_capacity_subgraph = nx.DiGraph()
    infinite_capacity_subgraph.add_nodes_from(nodes)
    infinite_capacity_subgraph.add_edges_from(
        (u, v) for u, v in G.edges() if capacity_key not in G[u][v]
    )

    if nx.has_path(infinite_capacity_subgraph, source, sink):
        try:
            nx.maximum_flow(
                G,
                source,
                sink,
                capacity=capacity_key,
                flow_func=flow_func,
            )
            assert False, "maximum_flow should raise NetworkXUnbounded"
        except NetworkXUnbounded:
            return

    flow_value, flow_dict = nx.maximum_flow(
        G,
        source,
        sink,
        capacity=capacity_key,
        flow_func=flow_func,
    )

    tol = 1e-7

    # Capacity constraints on every original directed edge.
    for u, v, attrs in G.edges(data=True):
        f = flow_dict[u][v]
        assert f >= -tol
        if capacity_key in attrs:
            assert f <= attrs[capacity_key] + tol

    def outflow(u):
        return sum(flow_dict[u].values())

    def inflow(u):
        return sum(flow_dict[pred][u] for pred in G.predecessors(u))

    # The documented flow_value is the net outflow from the source and,
    # equivalently, the net inflow to the sink.
    assert math.isclose(
        outflow(source) - inflow(source),
        flow_value,
        rel_tol=1e-7,
        abs_tol=1e-7,
    )
    assert math.isclose(
        inflow(sink) - outflow(sink),
        flow_value,
        rel_tol=1e-7,
        abs_tol=1e-7,
    )

    # Flow conservation at all non-terminal nodes.
    for node in nodes:
        if node not in (source, sink):
            assert math.isclose(
                inflow(node),
                outflow(node),
                rel_tol=1e-7,
                abs_tol=1e-7,
            )

    # Max-flow/min-cut consistency.
    cut_value = nx.minimum_cut_value(G, source, sink, capacity=capacity_key)
    assert math.isclose(flow_value, cut_value, rel_tol=1e-7, abs_tol=1e-7)

# End program