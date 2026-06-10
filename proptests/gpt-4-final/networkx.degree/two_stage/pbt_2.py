from hypothesis import given, strategies as st
from hypothesis.strategies import lists, integers
import networkx as nx

# Property 1: The output type should be a DegreeView object
@given(st.data())
def test_degree_output_type(data):
    G = nx.path_graph(data.draw(integers(min_value=0, max_value=100)))
    degree_view = nx.degree(G)
    assert isinstance(degree_view, nx.classes.reportviews.DegreeView)

# Property 2: The total degree of all nodes should equal twice the number of edges in the graph G
@given(st.data())
def test_degree_graph_property(data):
    G = nx.path_graph(data.draw(integers(min_value=0, max_value=100)))
    degree_view = nx.degree(G)
    total_degree = sum(deg for n, deg in degree_view)
    total_edges = G.number_of_edges()
    assert total_degree == 2 * total_edges

# Property 3: If 'nbunch' parameter is provided, the sum of degree of nodes in the output should be less than or equal to the sum of degree of all nodes when 'nbunch' is omitted
@given(st.data())
def test_degree_nbunch_property(data):
    G = nx.path_graph(data.draw(integers(min_value=0, max_value=100)))
    nbunch = [node for node in G.nodes() if data.draw(st.booleans())]
    degree_view = nx.degree(G, nbunch=nbunch)
    total_nbunch_degree = sum(deg for n, deg in degree_view)
    degree_view_all = nx.degree(G)
    total_degree_all = sum(deg for n, deg in degree_view_all)
    assert total_nbunch_degree <= total_degree_all

# Property 4: If 'weight' parameter is given, the degree of a particular node should be proportional to the sum of the weights of its edges
@given(st.data())
def test_degree_weight_property(data):
    G = nx.Graph()
    G.add_node(1)
    weights = [data.draw(integers(min_value=1, max_value=10)) for _ in range(5)]
    for weight in weights:
        G.add_edge(1, len(G.nodes), weight=weight)
    degree_view = nx.degree(G, weight='weight')
    assert degree_view[1] == sum(weights)

# Property 5: The degree of all nodes should be a non-negative integer
@given(st.data())
def test_degree_nonnegative_property(data):
    G = nx.path_graph(data.draw(integers(min_value=0, max_value=100)))
    degree_view = nx.degree(G)
    assert all(isinstance(deg, int) and deg >= 0 for n, deg in degree_view)

# End program