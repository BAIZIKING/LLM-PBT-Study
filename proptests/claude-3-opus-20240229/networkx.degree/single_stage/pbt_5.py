from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# Generate random directed and undirected graphs with a varying number of nodes and edges.
# The nbunch parameter is either None to compute degrees for all nodes, a single random node, 
# or a random subset of nodes. The weight parameter is either None or a random string.
# Check that the returned degree view is a dictionary where node degrees are non-negative integers. 
# If weight is specified, check that the degree values are the sums of edge weights.
@given(st.data())
def test_degree(data):
    # Generate random graph
    n_nodes = data.draw(st.integers(min_value=0, max_value=100))
    n_edges = data.draw(st.integers(min_value=0, max_value=n_nodes * (n_nodes - 1) // 2))
    g = nx.gnm_random_graph(n_nodes, n_edges, directed=data.draw(st.booleans()), seed=data.draw(st.integers()))

    # Generate random inputs
    nodes = g.nodes
    nbunch = data.draw(st.none() | st.sampled_from(nodes) | st.sets(st.sampled_from(nodes)))
    weight = data.draw(st.none() | st.text())
    
    degree_view = nx.degree(g, nbunch, weight)
    
    # Check return type is a dictionary
    assert isinstance(degree_view, dict)
    
    # Check degrees are non-negative integers
    assert all(isinstance(d, int) and d >= 0 for d in degree_view.values())
    
    if weight is None:
        # Check degree is number of edges for each node
        for n, d in degree_view.items():
            assert d == g.degree(n)
    else:
        # Check degree is sum of edge weights for each node 
        for n, d in degree_view.items():
            assert d == sum(attr.get(weight, 1) for _, _, attr in g.edges(n, data=True))
# End program