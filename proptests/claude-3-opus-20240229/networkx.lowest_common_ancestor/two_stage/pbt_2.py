from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_networkx_lowest_common_ancestor_properties(data):
    # Generate a random directed acyclic graph (DAG)
    num_nodes = data.draw(st.integers(min_value=1, max_value=100))
    edges = data.draw(st.lists(st.tuples(st.integers(min_value=0, max_value=num_nodes-1), 
                                         st.integers(min_value=0, max_value=num_nodes-1)), 
                               unique=True, min_size=1, max_size=num_nodes*2))
    G = nx.DiGraph(edges)
    
    # Property 1: If node1 and node2 are the same node, the function should return that node
    node = data.draw(st.integers(min_value=0, max_value=num_nodes-1))
    assert nx.lowest_common_ancestor(G, node, node) == node
    
    # Property 2: If node1 is an ancestor of node2, the function should return node1
    node1, node2 = data.draw(st.integers(min_value=0, max_value=num_nodes-1)), data.draw(st.integers(min_value=0, max_value=num_nodes-1))
    if nx.has_path(G, node1, node2):
        assert nx.lowest_common_ancestor(G, node1, node2) == node1
    
    # Property 3: If node2 is an ancestor of node1, the function should return node2
    node1, node2 = data.draw(st.integers(min_value=0, max_value=num_nodes-1)), data.draw(st.integers(min_value=0, max_value=num_nodes-1))
    if nx.has_path(G, node2, node1):
        assert nx.lowest_common_ancestor(G, node1, node2) == node2
    
    # Property 4: If node1 and node2 have no common ancestors and default is None, the function should return None
    node1, node2 = data.draw(st.integers(min_value=0, max_value=num_nodes-1)), data.draw(st.integers(min_value=0, max_value=num_nodes-1))
    if not nx.has_path(G, node1, node2) and not nx.has_path(G, node2, node1):
        assert nx.lowest_common_ancestor(G, node1, node2, default=None) is None
    
    # Property 5: The returned lowest common ancestor should be an ancestor of both node1 and node2
    node1, node2 = data.draw(st.integers(min_value=0, max_value=num_nodes-1)), data.draw(st.integers(min_value=0, max_value=num_nodes-1))
    lca = nx.lowest_common_ancestor(G, node1, node2)
    if lca is not None:
        assert nx.has_path(G, lca, node1) and nx.has_path(G, lca, node2)
# End program