from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_degree_sum_directed(data):
    graph = data.draw(st.graphs(graph_types=(nx.DiGraph, nx.MultiDiGraph)))
    in_degree_view = nx.degree(graph, weight=None)
    out_degree_view = nx.degree(graph, weight=None)
    total_in_degree = sum(degree for _, degree in in_degree_view)
    total_out_degree = sum(degree for _, degree in out_degree_view)
    assert total_in_degree == total_out_degree == len(graph.edges)
# End program