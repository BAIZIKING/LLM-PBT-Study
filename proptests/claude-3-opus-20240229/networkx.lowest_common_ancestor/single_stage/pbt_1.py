from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate a random directed graph with between 2-100 nodes
# - Randomly add 1-20 paths of length 1-10 to create edges and ancestry 
# - Randomly select 2 nodes to pass to lowest_common_ancestor
# - Use default=None to check behavior when no common ancestor exists
# - Check that return value is either None or a valid graph node
# - Check that return value is an ancestor of both input nodes
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    G = nx.DiGraph() 
    G.add_nodes_from(range(num_nodes))
    
    num_paths = data.draw(st.integers(min_value=1, max_value=20))
    for _ in range(num_paths):
        path_length = data.draw(st.integers(min_value=1, max_value=10))
        path = data.draw(st.permutations(range(num_nodes), path_length))
        nx.add_path(G, path)
    
    node1 = data.draw(st.sampled_from(list(G.nodes)))
    node2 = data.draw(st.sampled_from(list(G.nodes)))
    
    lca = nx.lowest_common_ancestor(G, node1, node2, default=None)
    
    assert (lca is None) or (lca in G.nodes)
    if lca is not None:
        assert nx.has_path(G, lca, node1) 
        assert nx.has_path(G, lca, node2)
# End program        