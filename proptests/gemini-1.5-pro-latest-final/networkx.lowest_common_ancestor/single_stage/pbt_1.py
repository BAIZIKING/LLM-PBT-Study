from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse directed graphs and node pairs to test lowest_common_ancestor
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # Generate a random directed graph
    graph_type = data.draw(st.sampled_from(["linear", "branched", "cyclic", "empty"]))
    if graph_type == "linear":
        G = nx.path_graph(data.draw(st.integers(min_value=2, max_value=10)))
    elif graph_type == "branched":
        G = nx.balanced_tree(2, data.draw(st.integers(min_value=1, max_value=3)))
    elif graph_type == "cyclic":
        G = nx.cycle_graph(data.draw(st.integers(min_value=3, max_value=10)))
    else:
        G = nx.DiGraph()

    # Generate node pairs, including edge cases
    nodes = list(G.nodes)
    node1, node2 = data.draw(
        st.tuples(
            st.sampled_from(nodes + [None]),  # Allow nodes not in the graph
            st.sampled_from(nodes + [None]),
        )
    )

    default_value = object()  # Unique default value for testing
    ancestor = nx.lowest_common_ancestor(G, node1, node2, default=default_value)

    # Check properties based on API documentation
    if ancestor is not default_value:
        assert nx.has_path(G, ancestor, node1)
        assert nx.has_path(G, ancestor, node2)
        for descendant in nx.descendants(G, ancestor):
            assert not (nx.has_path(G, descendant, node1) and nx.has_path(G, descendant, node2))
    else:
        assert not nx.all_pairs_lowest_common_ancestor(G, pairs=[(node1, node2)])  # No common ancestor

# End program