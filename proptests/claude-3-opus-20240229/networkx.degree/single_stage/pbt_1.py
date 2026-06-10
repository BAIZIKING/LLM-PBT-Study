from hypothesis import given, strategies as st
import networkx as nx

# Summary: Generate random directed graphs with varying numbers of nodes and edges.
# Use integers, tuples, and sets to generate node labels and edges. Check that:
# 1) The degree view dictionary includes all nodes in the graph
# 2) The degree for each node matches the number of edges to/from that node
# 3) Specifying a single node returns the degree for just that node
# 4) Specifying a weight returns the sum of edge weights for each node 
@given(st.data()) 
def test_degree(data):
    nodes = data.draw(st.sets(elements=st.integers(), min_size=0, max_size=100))
    edges = data.draw(st.sets(elements=st.tuples(st.sampled_from(nodes), st.sampled_from(nodes)), 
                              min_size=0, max_size=1000))
    G = nx.DiGraph() 
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    deg_view = nx.degree(G)
    assert set(deg_view.keys()) == set(G.nodes)
    for n, d in deg_view.items():
        assert d == G.in_degree(n) + G.out_degree(n)
    
    rand_node = data.draw(st.sampled_from(list(G.nodes)), label='rand_node')
    assert nx.degree(G, rand_node) == G.in_degree(rand_node) + G.out_degree(rand_node)

    rand_edge_weights = {(u,v): data.draw(st.integers(), label=f'({u},{v})') for u,v in G.edges}  
    nx.set_edge_attributes(G, rand_edge_weights, 'weight')
    deg_view_weighted = nx.degree(G, weight='weight')
    for n, d in deg_view_weighted.items():
        assert d == sum(rand_edge_weights[e] for e in G.in_edges(n)) + \
                    sum(rand_edge_weights[e] for e in G.out_edges(n))
# End program