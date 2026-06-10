from hypothesis import given, strategies as st
import networkx as nx

@given(st.graphs(), st.lists(elements=st.integers(), unique=True), st.lists(elements=st.integers()))
def test_networkx_degree_properties(graph, nbunch, weight):
    # Property 1: Test degree view of all nodes when nbunch=None
    degrees = nx.degree(graph)
    assert isinstance(degrees, dict) or isinstance(degrees, nx.classes.reportviews.DegreeView)
    assert len(degrees) == graph.number_of_nodes()

    # Property 2: Test degree view of specific node(s) when nbunch is given
    for node in nbunch:
        degrees = nx.degree(graph, nbunch=node)
        assert all(node in key for key in degrees.keys())

    # Property 3: Test output type of degree
    degrees = nx.degree(graph)
    assert isinstance(degrees, dict) or isinstance(degrees, nx.classes.reportviews.DegreeView)

    # Property 4: Test edge weights in degree calculation
    for w in weight:
        weights = {edge: w for edge in graph.edges()}
        nx.set_edge_attributes(graph, weights, 'weight')
        degrees = nx.degree(graph, weight='weight')
        for node, degree in degrees.items():
            assert degree == sum(w for edge,w in nx.get_node_attributes(graph,'weight').items() if node in edge)

    # Property 5: Test for handling of non-existent nodes in nbunch
    nbunch2 = [node for node in nbunch if node not in graph.nodes()]
    degrees = nx.degree(graph, nbunch=nbunch2)
    assert all(node not in degrees for node in nbunch2)