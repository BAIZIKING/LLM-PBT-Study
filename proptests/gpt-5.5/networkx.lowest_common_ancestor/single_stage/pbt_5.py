from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate small random directed acyclic graphs by choosing an integer
# node count and only allowing edges from lower-numbered nodes to higher-numbered
# nodes. This covers empty-edge graphs, disconnected components, isolated nodes,
# roots, leaves, chains, diamonds, equal node pairs, and pairs with/without common
# ancestors. Randomly choose node1, node2 from the graph and randomize default.
# Properties checked: if no common ancestor exists, the API returns default;
# otherwise, the result is a common ancestor and is "lowest", meaning no other
# common ancestor is reachable from it as a strict descendant.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    n = data.draw(st.integers(min_value=1, max_value=8), label="node_count")
    nodes = list(range(n))

    possible_edges = [(u, v) for u in nodes for v in nodes if u < v]
    if possible_edges:
        edges = data.draw(
            st.sets(st.sampled_from(possible_edges), max_size=len(possible_edges)),
            label="edges",
        )
    else:
        edges = set()

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    node1 = data.draw(st.sampled_from(nodes), label="node1")
    node2 = data.draw(st.sampled_from(nodes), label="node2")
    default = data.draw(
        st.one_of(
            st.none(),
            st.integers(),
            st.text(),
            st.tuples(st.text(), st.integers()),
        ),
        label="default",
    )

    result = nx.lowest_common_ancestor(G, node1, node2, default=default)

    ancestors1 = nx.ancestors(G, node1) | {node1}
    ancestors2 = nx.ancestors(G, node2) | {node2}
    common_ancestors = ancestors1 & ancestors2

    if not common_ancestors:
        assert result == default
    else:
        lowest_common_ancestors = {
            candidate
            for candidate in common_ancestors
            if not any(
                other != candidate and nx.has_path(G, candidate, other)
                for other in common_ancestors
            )
        }

        assert result in common_ancestors
        assert result in lowest_common_ancestors
# End program