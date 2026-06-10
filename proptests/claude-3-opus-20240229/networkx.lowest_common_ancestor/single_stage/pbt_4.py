from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate a random directed graph by adding edges between random nodes
# - Pick two random nodes from the graph 
# - Check that lowest_common_ancestor returns a node if the nodes have a common ancestor
#   or returns the default value if they don't
# - As an edge case, use the same node for both node1 and node2 and check the function returns that node
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # Generate random graph
    nodes = data.draw(st.lists(st.integers(), min_size=2, max_size=100, unique=True))
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for _ in range(data.draw(st.integers(min_value=1, max_value=len(nodes)**2))):
        u, v = data.draw(st.sampled_from(nodes), st.sampled_from(nodes))
        G.add_edge(u, v)
    
    # Pick random nodes
    node1 = data.draw(st.sampled_from(nodes))
    node2 = data.draw(st.sampled_from(nodes))
    default = data.draw(st.none() | st.integers())
    
    # Check properties
    ancestor = nx.lowest_common_ancestor(G, node1, node2, default)
    if ancestor is not default:
        assert nx.has_path(G, ancestor, node1) 
        assert nx.has_path(G, ancestor, node2)
    else:
        assert not nx.has_path(G, node1, node2) and not nx.has_path(G, node2, node1)
    
    # Edge case
    assert nx.lowest_common_ancestor(G, node1, node1) == node1
# End program