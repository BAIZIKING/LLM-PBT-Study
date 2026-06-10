from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_lowest_common_ancestor_properties(data):
    # Generate a random directed graph
    max_nodes = 100
    G = nx.gnp_random_graph(data.draw(st.integers(1, max_nodes)), 0.5, directed=True)
    
    # Generate two random nodes from the graph
    node1, node2 = data.draw(st.sampled_from(list(G.nodes())), 2)
    
    # Generate a random default value
    default = data.draw(st.none() | st.integers())
    
    # Property 1: Output should be either node1, node2, one of their ancestors, or the default value
    assert nx.lowest_common_ancestor(G, node1, node2, default) in [node1, node2, default] + list(nx.ancestors(G, node1)) + list(nx.ancestors(G, node2))
    
    # Property 2: If node1 is an ancestor of node2, the output should be node1
    if node1 in nx.ancestors(G, node2):
        assert nx.lowest_common_ancestor(G, node1, node2) == node1
    
    # Property 3: If node2 is an ancestor of node1, the output should be node2
    if node2 in nx.ancestors(G, node1):
        assert nx.lowest_common_ancestor(G, node1, node2) == node2
    
    # Property 4: If node1 and node2 have no common ancestors and a default value is provided, the output should be the default value
    if not set(nx.ancestors(G, node1)) & set(nx.ancestors(G, node2)) and default is not None:
        assert nx.lowest_common_ancestor(G, node1, node2, default) == default
    
    # Property 5: If node1 and node2 are the same node, the output should be that node
    if node1 == node2:
        assert nx.lowest_common_ancestor(G, node1, node2) == node1
# End program