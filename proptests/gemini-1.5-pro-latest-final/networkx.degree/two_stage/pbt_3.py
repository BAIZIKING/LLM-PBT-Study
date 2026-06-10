from hypothesis import given, strategies as st
import networkx as nx

# Define strategies for graph generation and node selection
graph_strategy = st.graphs(nodes=st.integers(min_value=1, max_value=100), 
                           edges=st.tuples(st.integers(), st.integers()))

@given(graph_strategy)
def test_non_negative_degree(graph):
    for node, degree in nx.degree(graph):
        assert degree >= 0
# End program

@given(graph_strategy)
def test_max_degree(graph):
    max_degree = max(dict(nx.degree(graph)).values())
    num_nodes = len(graph.nodes())
    assert max_degree <= num_nodes - 1
# End program

@given(graph_strategy)
def test_degree_sum(graph):
    degree_sum = sum(dict(nx.degree(graph)).values())
    num_edges = len(graph.edges())
    assert degree_sum == 2 * num_edges
# End program

@given(st.graphs(is_directed=False)) # Undirected graphs only
def test_degree_symmetry(graph):
    for node in graph.nodes():
        assert graph.degree(node) == list(nx.degree(graph)).count(node)
# End program

@given(st.graphs(is_directed=True)) # Directed graphs only
def test_degree_correspondence(graph):
    for node, (in_degree, out_degree) in graph.in_degree(), graph.out_degree():
        assert in_degree + out_degree == graph.degree(node, weight=None)
# End program 