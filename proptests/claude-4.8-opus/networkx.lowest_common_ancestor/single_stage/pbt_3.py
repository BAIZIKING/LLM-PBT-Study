from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random DAGs by selecting N nodes (0..N-1) and only adding
# edges from lower-indexed to higher-indexed nodes (guaranteeing acyclicity).
# Sample node1/node2 from the existing nodes (allowing equality). Use a sentinel
# default. Check: (1) result is a node or default, (2) symmetry, (3) the result
# is a valid common ancestor (incl. self), and (4) it is the lowest such ancestor.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    n = data.draw(st.integers(min_value=1, max_value=8))
    nodes = list(range(n))

    # Generate acyclic edges: only i -> j where i < j
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = data.draw(
        st.lists(st.sampled_from(possible_edges), unique=True)
        if possible_edges else st.just([])
    )

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    assert nx.is_directed_acyclic_graph(G)

    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nodes))

    sentinel = object()
    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)

    # Helper: ancestors of a node including the node itself
    def anc_incl(node):
        return nx.ancestors(G, node) | {node}

    common = anc_incl(node1) & anc_incl(node2)

    # Property 1: result is a node in G or the default sentinel
    if result is sentinel:
        # If default returned, there must be no common ancestor
        assert len(common) == 0
    else:
        assert result in G.nodes

        # Property 3: result must be a valid common ancestor
        assert result in common

        # Property 4: result must be the lowest common ancestor, i.e. none of
        # its proper descendants are also common ancestors.
        descendants = nx.descendants(G, result)
        assert descendants.isdisjoint(common)

    # Property 2: symmetry
    result_swapped = nx.lowest_common_ancestor(G, node2, node1, default=sentinel)
    assert result == result_swapped
# End program