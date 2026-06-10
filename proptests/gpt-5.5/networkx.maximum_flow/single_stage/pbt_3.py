from hypothesis import given, strategies as st
import math
import pytest
import networkx as nx
from networkx.algorithms.flow import edmonds_karp, preflow_push, shortest_augmenting_path

# Summary: Generate three documented input classes:
# 1) finite-capacity DiGraphs with random node labels, edge sets, capacity attribute names,
#    capacities, flow_func choices, and safe algorithm-specific kwargs;
# 2) DiGraphs with a missing-capacity s->t edge, which represents an infinite-capacity path;
# 3) MultiDiGraphs, which maximum_flow explicitly does not support.
#
# Properties checked:
# - Unsupported MultiGraphs raise NetworkXError.
# - Infinite-capacity s-t paths raise NetworkXUnbounded.
# - For finite-capacity graphs, returned flows obey capacity constraints and flow conservation.
# - The returned flow_value equals net outflow from the source.
# - The returned flow_value agrees with maximum_flow_value and minimum_cut_value.

@given(st.data())
def test_networkx_maximum_flow(data):
    case = data.draw(st.sampled_from(["finite", "unbounded", "multigraph"]))

    n = data.draw(st.integers(min_value=2, max_value=7))
    nodes = data.draw(
        st.lists(
            st.one_of(st.integers(min_value=-20, max_value=20), st.text(min_size=0, max_size=4)),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )
    s = data.draw(st.sampled_from(nodes))
    t = data.draw(st.sampled_from([node for node in nodes if node != s]))

    capacity_attr = data.draw(st.sampled_from(["capacity", "cap", "bandwidth", "c"]))
    flow_func = data.draw(st.sampled_from([None, edmonds_karp, preflow_push, shortest_augmenting_path]))

    finite_capacity = st.one_of(
        st.integers(min_value=0, max_value=20),
        st.floats(min_value=0, max_value=20, allow_nan=False, allow_infinity=False, width=32),
    )

    if case == "multigraph":
        G = nx.MultiDiGraph()
        G.add_nodes_from(nodes)

        possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                min_size=0,
                max_size=min(12, len(possible_edges)),
            )
        )
        for u, v in edges:
            G.add_edge(u, v, **{capacity_attr: data.draw(finite_capacity)})

        with pytest.raises(nx.NetworkXError):
            nx.maximum_flow(G, s, t, capacity=capacity_attr, flow_func=flow_func)
        return

    if case == "unbounded":
        G = nx.DiGraph()
        G.add_nodes_from(nodes)

        possible_edges = [(u, v) for u in nodes for v in nodes if u != v and (u, v) != (s, t)]
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                unique=True,
                min_size=0,
                max_size=min(12, len(possible_edges)),
            )
        )
        for u, v in edges:
            G.add_edge(u, v, **{capacity_attr: data.draw(finite_capacity)})

        # Missing capacity_attr means infinite capacity, so this is an infinite-capacity s-t path.
        G.add_edge(s, t)

        with pytest.raises(nx.NetworkXUnbounded):
            nx.maximum_flow(G, s, t, capacity=capacity_attr, flow_func=flow_func)
        return

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    possible_edges = [(u, v) for u in nodes for v in nodes if u != v]
    edges = data.draw(
        st.lists(
            st.sampled_from(possible_edges),
            unique=True,
            min_size=0,
            max_size=min(14, len(possible_edges)),
        )
    )

    total_capacity = 0.0
    for u, v in edges:
        cap = data.draw(finite_capacity)
        total_capacity += float(cap)
        G.add_edge(u, v, **{capacity_attr: cap})

    kwargs = {}
    if flow_func is edmonds_karp:
        kwargs["cutoff"] = total_capacity + 1.0
    elif flow_func is preflow_push:
        kwargs["global_relabel_freq"] = data.draw(st.sampled_from([1, 2]))
    elif flow_func is shortest_augmenting_path:
        kwargs["two_phase"] = data.draw(st.booleans())

    flow_value, flow_dict = nx.maximum_flow(
        G,
        s,
        t,
        capacity=capacity_attr,
        flow_func=flow_func,
        **kwargs,
    )

    tol = 1e-7

    for u, v, attrs in G.edges(data=True):
        assert u in flow_dict
        assert v in flow_dict[u]

        edge_flow = flow_dict[u][v]
        edge_capacity = attrs[capacity_attr]

        assert edge_flow >= -tol
        assert edge_flow <= edge_capacity + tol

    for node in G.nodes:
        outflow = sum(flow_dict[node].values())
        inflow = sum(flow_dict[pred][node] for pred in G.predecessors(node))
        net_outflow = outflow - inflow

        if node == s:
            assert math.isclose(net_outflow, flow_value, rel_tol=tol, abs_tol=tol)
        elif node == t:
            assert math.isclose(-net_outflow, flow_value, rel_tol=tol, abs_tol=tol)
        else:
            assert math.isclose(net_outflow, 0.0, rel_tol=tol, abs_tol=tol)

    value_only = nx.maximum_flow_value(
        G,
        s,
        t,
        capacity=capacity_attr,
        flow_func=flow_func,
        **kwargs,
    )
    cut_value = nx.minimum_cut_value(
        G,
        s,
        t,
        capacity=capacity_attr,
        flow_func=flow_func,
        **kwargs,
    )

    assert math.isclose(flow_value, value_only, rel_tol=tol, abs_tol=tol)
    assert math.isclose(flow_value, cut_value, rel_tol=tol, abs_tol=tol)

# End program