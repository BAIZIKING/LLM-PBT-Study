from hypothesis import given, strategies as st
import networkx as nx

# Summary: Build random DAGs by adding forward-only edges (i < j) to guarantee
# acyclicity, then pick two arbitrary nodes (possibly equal) plus a unique
# sentinel default. Verify the documented contract: when no common ancestor
# exists the default is returned; otherwise the result is a genuine common
# ancestor that is the "lowest" (no other common ancestor is its descendant).
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    n = data.draw(st.integers(min_value=1, max_value=8), label="num_nodes")
    nodes = list(range(n))

    # Forward-only candidate edges keep the graph acyclic (a DAG).
    candidate_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = data.draw(
        st.lists(st.sampled_from(candidate_edges), unique=True)
        if candidate_edges else st.just([]),
        label="edges",
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    node1 = data.draw(st.sampled_from(nodes), label="node1")
    node2 = data.draw(st.sampled_from(nodes), label="node2")

    sentinel = "NO_COMMON_ANCESTOR_SENTINEL"

    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)

    # Helper: ancestors of a node, including the node itself (a node is
    # considered its own ancestor for LCA purposes, as shown in the docs).
    def ancestors_inclusive(node):
        anc = set(nx.ancestors(G, node))
        anc.add(node)
        return anc

    anc1 = ancestors_inclusive(node1)
    anc2 = ancestors_inclusive(node2)
    common = anc1 & anc2

    if not common:
        # Property 1: no common ancestor -> must return the default.
        assert result == sentinel
    else:
        # Property 2: result must be a genuine common ancestor.
        assert result != sentinel
        assert result in common, (
            f"Result {result} is not a common ancestor of {node1}, {node2}"
        )

        # Property 3: "lowest" -> no other common ancestor is a strict
        # descendant of the returned LCA.
        descendants_of_result = nx.descendants(G, result)
        for c in common:
            if c != result:
                assert c not in descendants_of_result, (
                    f"Found common ancestor {c} below the returned LCA {result}"
                )
# End program