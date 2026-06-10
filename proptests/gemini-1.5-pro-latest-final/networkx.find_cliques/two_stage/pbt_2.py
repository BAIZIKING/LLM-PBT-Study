from hypothesis import given, strategies as st
import networkx

@given(graphs_and_nodes())
def test_networkx_find_cliques_property_5(graph_and_nodes):
    graph, nodes = graph_and_nodes
    if nodes is not None:
        for clique in nx.find_cliques(graph, nodes=nodes):
            assert all(node in clique for node in nodes)
# End program