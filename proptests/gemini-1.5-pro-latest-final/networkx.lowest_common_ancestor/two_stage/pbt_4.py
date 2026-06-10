from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_lowest_common_ancestor_property_5(data):
    graph = data.draw(st.graphs(graph_type=nx.DiGraph, min_size=2))
    node1 = data.draw(st.sampled_from(list(graph.nodes)))
    node2 = data.draw(st.sampled_from(list(graph.successors(node1))))
    default_value = data.draw(st.integers())
    output = nx.lowest_common_ancestor(graph, node1, node2, default=default_value)
    assert output == node1
# End program 