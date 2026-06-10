from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate small random directed acyclic graphs by first generating
# unique hashable node labels, then only allowing edges from earlier nodes to
# later nodes. This creates valid DAGs while still covering isolated nodes,
# disconnected components, single-node graphs, paths, diamonds, sparse graphs,
# and dense graphs. node1 and node2 are always drawn from the graph, as required
# by the API, and default is also varied across None and other hashable values.
#
# Properties checked:
# 1. If node1 and node2 have no common ancestor, the function returns default.
# 2. Otherwise, the returned node is a common ancestor of node1 and node2.
# 3. The returned node is "lowest": no other common ancestor is reachable from it.
# 4. The same properties hold when node1 and node2 are passed in reverse order.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    node_strategy = st.one_of(
        st.integers(min_value=-20, max_value=20),
        st.text(min_size=0, max_size=4),
        st.tuples(st.integers(min_value=-5, max_value=5), st.text(min_size=0, max_size=3)),
    )

    n = data.draw(st.integers(min_value=1, max_value=8), label="number_of_nodes")
    nodes = data.draw(
        st.lists(node_strategy, min_size=n, max_size=n, unique=True),
        label="nodes",
    )

    possible_edges = [
        (nodes[i], nodes[j])
        for i in range(len(nodes))
        for j in range(i + 1, len(nodes))
    ]

    if possible_edges:
        edges = data.draw(
            st.lists(
                st.sampled_from(possible_edges),
                min_size=0,
                max_size=len(possible_edges),
                unique=True,
            ),
            label="edges",
        )
    else:
        edges = []

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    node1 = data.draw(st.sampled_from(nodes), label="node1")
    node2 = data.draw(st.sampled_from(nodes), label="node2")

    default = data.draw(
        st.one_of(
            st.none(),
            node_strategy,
            st.tuples(st.just("__default__"), st.integers(min_value=-10, max_value=10)),
        ),
        label="default",
    )

    ancestors1 = nx.ancestors(G, node1) | {node1}
    ancestors2 = nx.ancestors(G, node2) | {node2}
    common_ancestors = ancestors1 & ancestors2

    expected_lowest_ancestors = {
        ancestor
        for ancestor in common_ancestors
        if not any(
            ancestor != other and nx.has_path(G, ancestor, other)
            for other in common_ancestors
        )
    }

    result = nx.lowest_common_ancestor(G, node1, node2, default=default)
    reversed_result = nx.lowest_common_ancestor(G, node2, node1, default=default)

    if not common_ancestors:
        assert result is default
        assert reversed_result is default
    else:
        assert result in expected_lowest_ancestors
        assert reversed_result in expected_lowest_ancestors
# End program