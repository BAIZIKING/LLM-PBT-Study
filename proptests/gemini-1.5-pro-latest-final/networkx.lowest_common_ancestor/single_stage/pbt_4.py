from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates diverse directed graphs and node pairs to test lowest_common_ancestor
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # Generate graph types and sizes
    graph_types = st.sampled_from([nx.DiGraph, nx.random_tree, nx.gnp_random_graph])
    graph_size = st.integers(min_value=2, max_value=50)
    graph = data.draw(graph_types(graph_size))

    # Generate node pairs
    nodes = list(graph.nodes)
    node_pairs = st.tuples(st.sampled_from(nodes), st.sampled_from(nodes))
    node1, node2 = data.draw(node_pairs)

    # Get the lowest common ancestor or default
    default_value = "No Common Ancestor"
    ancestor = nx.lowest_common_ancestor(graph, node1, node2, default=default_value)

    # Check properties
    if ancestor != default_value:
        assert nx.has_path(graph, ancestor, node1)
        assert nx.has_path(graph, ancestor, node2)
        # Additional checks for lowest property can be implemented here

# End program