from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random DAGs by creating integer nodes and only adding
# edges (u, v) with u < v to guarantee acyclicity. Query nodes are sampled
# from existing nodes so they are always valid, covering equal-node, shared-
# ancestor, and no-common-ancestor cases. A unique sentinel marks "no ancestor".
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # Generate nodes
    n = data.draw(st.integers(min_value=1, max_value=12))
    nodes = list(range(n))

    # Generate edges (u, v) with u < v to ensure a DAG (acyclic)
    possible_edges = [(u, v) for u in nodes for v in nodes if u < v]
    edges = data.draw(
        st.lists(st.sampled_from(possible_edges), unique=True)
        if possible_edges else st.just([])
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Pick two query nodes (may be equal)
    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nodes))

    sentinel = object()
    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)

    # Helper: ancestors of x including x itself
    def anc_incl(x):
        return nx.ancestors(G, x) | {x}

    anc1 = anc_incl(node1)
    anc2 = anc_incl(node2)
    common = anc1 & anc2

    if result is sentinel:
        # Property 1: default returned only when there is no common ancestor
        assert len(common) == 0
    else:
        # Property 2: result must be a node in the graph
        assert result in G

        # Property 3: result is a common ancestor of both nodes
        assert result in common

        # Property 4 ("lowest"): no other common ancestor is a
        # descendant of the result (none strictly lower than the LCA)
        descendants_of_lca = nx.descendants(G, result)
        for c in common:
            if c == result:
                continue
            # c must NOT be strictly below the chosen LCA
            assert c not in descendants_of_lca

    # Property 5: symmetry of the LCA relation
    result_sym = nx.lowest_common_ancestor(G, node2, node1, default=sentinel)
    if result is sentinel:
        assert result_sym is sentinel
    else:
        assert result == result_sym
# End program