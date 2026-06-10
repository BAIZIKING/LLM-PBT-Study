from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates random directed graphs and node pairs to test lowest_common_ancestor.
@given(
    graph=st.builds(
        lambda n, p: nx.gnp_random_graph(n, p, directed=True),
        st.integers(min_value=0, max_value=10),
        st.floats(min_value=0.0, max_value=1.0),
    ),
    node1=st.integers(),
    node2=st.integers(),
)
def test_networkx_lowest_common_ancestor(graph, node1, node2):
    # Ensure nodes belong to the same connected component
    if not nx.has_path(graph, node1, node2):
        return

    ancestor = nx.lowest_common_ancestor(graph, node1, node2)

    # Check if ancestor is None or a valid ancestor
    if ancestor is None:
        assert not any(nx.has_path(graph, common_node, node1) and nx.has_path(graph, common_node, node2) for common_node in graph.nodes)
    else:
        assert nx.has_path(graph, ancestor, node1) and nx.has_path(graph, ancestor, node2)

        # Check if ancestor is the lowest (shortest path)
        for common_node in graph.nodes:
            if nx.has_path(graph, common_node, node1) and nx.has_path(graph, common_node, node2):
                ancestor_path_len = nx.shortest_path_length(graph, ancestor, node1) + nx.shortest_path_length(graph, ancestor, node2)
                common_path_len = nx.shortest_path_length(graph, common_node, node1) + nx.shortest_path_length(graph, common_node, node2)
                assert ancestor_path_len <= common_path_len

# End program