from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generates random directed graphs and node pairs, testing properties of lowest common ancestor.
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # Generate random graph configurations.
    graph_size = data.draw(st.integers(min_value=0, max_value=20))
    graph_p = data.draw(st.floats(min_value=0.0, max_value=1.0))
    graph_type = data.draw(st.sampled_from([nx.gn_graph, nx.gnp_random_graph]))
    g = graph_type(graph_size, graph_p, directed=True)

    # Select node pairs, including potentially invalid pairs.
    node_list = list(g.nodes)
    node1 = data.draw(st.sampled_from(node_list + [None]))
    node2 = data.draw(st.sampled_from(node_list + [None]))

    default_value = object()
    ancestor = nx.lowest_common_ancestor(g, node1, node2, default=default_value)

    if ancestor != default_value:
        assert nx.has_path(g, ancestor, node1)
        assert nx.has_path(g, ancestor, node2)
        for descendant in nx.descendants(g, ancestor):
            assert not (nx.has_path(g, descendant, node1) and nx.has_path(g, descendant, node2))
    else:
        assert not nx.has_path(g, node1, node2)

# End program