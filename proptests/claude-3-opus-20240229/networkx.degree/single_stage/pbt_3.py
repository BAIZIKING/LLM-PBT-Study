from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate random Graph objects using nx.Graph() and adding random nodes/edges
# - Generate random subset of nodes to pass as nbunch
# - Randomly decide whether to specify weight parameter
# - Check that:
#   1) Number of items in returned degree view dict equals number of nodes in nbunch (or total nodes in G if nbunch not specified)  
#   2) Degree values are non-negative integers
#   3) Degree values are <= total number of nodes - 1
#   4) If weight not specified, degree values represent number of edges to/from each node
#   5) If weight specified, degree values represent sum of edge weights to/from each node
@given(st.data())
def test_degree(data):
    # Generate random graph
    G = nx.Graph()
    num_nodes = data.draw(st.integers(min_value=0, max_value=100))
    nodes = data.draw(st.lists(st.integers(), min_size=num_nodes, max_size=num_nodes, unique=True))
    G.add_nodes_from(nodes)
    num_edges = data.draw(st.integers(min_value=0, max_value=num_nodes*(num_nodes-1)//2))
    edges = data.draw(st.lists(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), unique=True, min_size=num_edges, max_size=num_edges))
    G.add_edges_from(edges)

    # Generate nbunch and weight parameters
    nbunch = data.draw(st.one_of(st.none(), st.lists(st.sampled_from(nodes), unique=True)))
    use_weight = data.draw(st.booleans())
    weight = 'weight' if use_weight else None
    if use_weight:
        for u,v in G.edges:
            G[u][v]['weight'] = data.draw(st.integers(min_value=1, max_value=10))

    degrees = nx.degree(G, nbunch, weight)
    if nbunch is None:
        nbunch = G.nodes

    # Check properties
    assert len(degrees) == len(nbunch)
    for _, d in degrees:
        assert isinstance(d, int)
        assert d >= 0
        assert d <= len(G) - 1
        if weight is None:
            assert d <= G.degree(nbunch) 
        else:
            assert d == sum(e[weight] for _, e in G[n].items() if weight in e)
# End program