from hypothesis import given, strategies as st
import networkx as nx

# Summary: Build a random DAG by adding edges only from lower-indexed to higher-indexed
# nodes (guaranteeing acyclicity), vary node count and edge density, then sample two
# nodes (possibly equal) and a sentinel default. Check membership, the common-ancestor
# property, symmetry, and self-LCA.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # Generate nodes
    n = data.draw(st.integers(min_value=1, max_value=8), label="num_nodes")
    nodes = list(range(n))

    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    # Add forward edges (u < v) to guarantee a DAG
    for u in nodes:
        for v in nodes:
            if u < v:
                if data.draw(st.booleans(), label=f"edge_{u}_{v}"):
                    G.add_edge(u, v)

    # Sample two nodes (possibly equal)
    node1 = data.draw(st.sampled_from(nodes), label="node1")
    node2 = data.draw(st.sampled_from(nodes), label="node2")

    sentinel = object()

    result = nx.lowest_common_ancestor(G, node1, node2, default=sentinel)
    result_sym = nx.lowest_common_ancestor(G, node2, node1, default=sentinel)

    # Property 3: Symmetry
    assert result == result_sym

    if result is sentinel:
        # No common ancestor reported; verify there genuinely is none.
        anc1 = nx.ancestors(G, node1) | {node1}
        anc2 = nx.ancestors(G, node2) | {node2}
        assert len(anc1 & anc2) == 0
    else:
        # Property 1: Returned value must be a node in the graph
        assert result in G.nodes

        # Property 2: result must be a common ancestor of both nodes
        anc1 = nx.ancestors(G, node1) | {node1}
        anc2 = nx.ancestors(G, node2) | {node2}
        assert result in anc1
        assert result in anc2

        # Property 4: Self LCA
        if node1 == node2:
            assert result == node1
# End program