from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_degree(data):
    # randomly generate nodes and edges
    nodes = data.draw(st.lists(st.integers()))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes))))
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # randomly generate nbunch and weight
    nbunch = data.draw(st.one_of(st.sampled_from(nodes), st.lists(st.sampled_from(nodes))))
    weight = data.draw(st.one_of(st.none(), st.text()))
    
    # get degree view
    degree_view = nx.degree(G, nbunch=nbunch, weight=weight)
    
    if nbunch is None:
        # check whether the returned degree view is over all nodes
        assert len(degree_view) == len(nodes)
    elif isinstance(nbunch, list):
        # check whether the returned degree view is over the given nbunch
        assert len(degree_view) == len(nbunch)
    else:
        # check whether the returned degree view is over the given single node
        assert len(degree_view) == 1
# End program