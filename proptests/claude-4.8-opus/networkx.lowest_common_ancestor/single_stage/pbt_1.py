from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate a random DAG by creating N integer nodes and only adding edges
# from lower-indexed to higher-indexed nodes (guaranteeing acyclicity), with random
# density. Pick node1 and node2 from existing nodes (allowing equal nodes and
# disconnected components). Check that the returned LCA is either the default sentinel
# or a valid common ancestor that is genuinely the "lowest" (no descendant common
# ancestor exists), and that equal nodes return themselves.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    n = data.draw(st.integers(min_value=1, max_value=8), label="num_nodes")
    nodes = list(range(n))

    # All possible DAG edges (low -> high index) keep the graph acyclic.
    possible_edges = [(u, v) for u in nodes for v in nodes if u < v]
    edges = data.draw(
        st.lists(st.sampled_from(possible_edges), unique=True)
        if possible_edges else st.just([]),
        label="edges",
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    node1 = data.draw(st.sampled_from(nodes), label="node1")
    node2 = data.draw(st.sampled_from(nodes), label="node2")

    sentinel = "NO_COMMON_ANCESTOR_SENTINEL"
    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)

    # "Ancestors of x including x itself" — the set of valid common ancestors.
    anc1 = nx.ancestors(G, node1) | {node1}
    anc2 = nx.ancestors(G, node2) | {node2}
    common = anc1 & anc2

    if not common:
        # Property: when no common ancestor exists, default is returned.
        assert result == sentinel
    else:
        # Property: a returned LCA must be an actual node in the graph.
        assert result in G

        # Property: the LCA must be a common ancestor of both nodes.
        assert result in common

        # Property ("lowest"): no other common ancestor is a descendant of the
        # returned LCA, i.e. the LCA is the deepest common ancestor.
        descendants_of_lca = nx.descendants(G, result)
        deeper_common = (common & descendants_of_lca)
        assert not deeper_common, (
            f"Found common ancestor(s) {deeper_common} deeper than reported "
            f"LCA {result}"
        )

        # Property (self-LCA): identical nodes are their own lowest common ancestor.
        if node1 == node2:
            assert result == node1
# End program