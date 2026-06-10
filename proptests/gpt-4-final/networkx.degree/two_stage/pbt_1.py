from hypothesis import given, strategies as st
import networkx as nx

@given(G=st.dictionaries(st.integers(), st.integers()), node=st.integers(), weight=st.integers())
def test_networkx_degree_property(G, node, weight):
    graph = nx.DiGraph(G)
    try:
        # test property 3
        deg = nx.degree(graph, node, weight)
        assert isinstance(deg, int), "Degree should be an integer"
        assert 0 <= deg <= graph.number_of_nodes() - 1, "Degree should be within [0, n-1]"
        # test property 4
        assert type(deg) is int, 'Output should be integer when single node is passed'
        # test property 2
        assert len(nx.degree(graph)) == graph.number_of_nodes(), "Degree function's output should equal to the total number of nodes in the graph G when 'nbunch' argument is None"
    except: # node is not in the graph
        pass

@given(G=st.dictionaries(st.integers(), st.floats()), node=st.integers(), weight=st.floats())
def test_networkx_weighted_degree_property(G, node, weight):
    graph = nx.DiGraph(G)
    try:
        # test property 5
        deg = nx.degree(graph, node, weight)
        assert isinstance(deg, (int, float)), "Weighted degree should be an integer or float"
    except: # node is not in the graph
        pass
# End program