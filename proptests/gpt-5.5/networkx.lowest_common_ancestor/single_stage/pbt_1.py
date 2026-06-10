from hypothesis import given, strategies as st
import networkx as nx

NODE_STRATEGY = st.one_of(
    st.integers(min_value=-50, max_value=50),
    st.text(min_size=0, max_size=6),
    st.tuples(st.integers(min_value=-10, max_value=10), st.text(max_size=3)),
)

DEFAULT_STRATEGY = st.one_of(
    st.none(),
    st.integers(min_value=-100, max_value=100),
    st.text(max_size=8),
    st.lists(st.integers(min_value=-5, max_value=5), max_size=3),
)

# Summary: Generate nonempty directed acyclic graphs by choosing unique hashable
# node labels and adding only forward edges in a chosen topological order. Mix
# empty, chain, complete, fan-in, fan-out, and random DAG shapes to cover
# disconnected graphs, isolated nodes, ancestor/descendant pairs, same-node
# pairs, and no-common-ancestor cases. Choose node1 and node2 from G, sometimes
# forcing them equal. Generate varied default values. Properties checked:
# if no reflexive common ancestor exists, the API returns default; otherwise it
# returns a common ancestor that is lowest, meaning no other common ancestor is a
# strict descendant of it.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    n = data.draw(st.integers(min_value=1, max_value=8), label="node_count")
    nodes = data.draw(
        st.lists(NODE_STRATEGY, min_size=n, max_size=n, unique=True),
        label="nodes",
    )

    shape = data.draw(
        st.sampled_from(["empty", "chain", "complete", "fan_in", "fan_out", "random"]),
        label="dag_shape",
    )

    possible_edges = [(nodes[i], nodes[j]) for i in range(n) for j in range(i + 1, n)]

    if shape == "empty":
        edges = []
    elif shape == "chain":
        edges = [(nodes[i], nodes[i + 1]) for i in range(n - 1)]
    elif shape == "complete":
        edges = possible_edges
    elif shape == "fan_in":
        edges = [(nodes[i], nodes[-1]) for i in range(n - 1)]
    elif shape == "fan_out":
        edges = [(nodes[0], nodes[j]) for j in range(1, n)]
    else:
        edges = data.draw(
            st.sets(st.sampled_from(possible_edges), max_size=len(possible_edges))
            if possible_edges
            else st.just(set()),
            label="random_edges",
        )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    node1 = data.draw(st.sampled_from(nodes), label="node1")
    node2 = data.draw(st.one_of(st.just(node1), st.sampled_from(nodes)), label="node2")

    sentinel = object()
    default = data.draw(
        st.one_of(DEFAULT_STRATEGY, st.just(sentinel)),
        label="default",
    )

    result = nx.lowest_common_ancestor(G, node1, node2, default=default)

    ancestors1 = nx.ancestors(G, node1) | {node1}
    ancestors2 = nx.ancestors(G, node2) | {node2}
    common_ancestors = ancestors1 & ancestors2

    if not common_ancestors:
        assert result is default or result == default
    else:
        lowest_common_ancestors = {
            candidate
            for candidate in common_ancestors
            if not any(
                candidate != other and nx.has_path(G, candidate, other)
                for other in common_ancestors
            )
        }

        assert result in common_ancestors
        assert result in lowest_common_ancestors

# End program