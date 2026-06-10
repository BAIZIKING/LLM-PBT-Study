from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate a random graph with nodes and edges. The number of nodes and edges are 
# both drawn from integers between 0 and 100. Edges are tuples of node pairs. Node ids
# are sequential integers from 0 to num_nodes-1. This covers small and large graphs,
# graphs with no edges, and graphs with many edges. nbunch is either None to compute 
# degrees of all nodes, a single random node id, or a random subset of node ids.

@given(st.data())
def test_degree(data):
    num_nodes = data.draw(st.integers(min_value=0, max_value=100))
    nodes = range(num_nodes)
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), 
                               max_size=100))
    G = nx.Graph()
    G.add_nodes_from(nodes) 
    G.add_edges_from(edges)
    
    nbunch_type = data.draw(st.sampled_from(['all', 'single', 'multiple']))
    if nbunch_type == 'all':
        nbunch = None
    elif nbunch_type == 'single':
        nbunch = data.draw(st.sampled_from(nodes))
    else:
        nbunch = data.draw(st.lists(st.sampled_from(nodes), min_size=1, max_size=len(nodes)))
    
    degree_view = nx.degree(G, nbunch)
    
    if nbunch is None:
        assert len(degree_view) == len(nodes)
    elif isinstance(nbunch, int):
        assert len(degree_view) == 1
        assert nbunch in degree_view
    else:
        assert len(degree_view) == len(nbunch)
        assert set(nbunch) == set(degree_view.keys())
        
    for node, degree in degree_view.items():
        assert degree >= 0
        assert degree <= len(nodes) - 1
        assert degree == len(G.edges(node))
# End program