
@given(st.data())
def test_networkx_lowest_common_ancestor_property_5(data):
    graph = data.draw(st.graphs(graph_type=networkx.DiGraph))
    node1 = data.draw(st.sampled_from(list(graph.nodes)))
    lca = networkx.lowest_common_ancestor(graph, node1, node1)
    assert lca == node1
# End program