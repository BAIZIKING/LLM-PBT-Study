from hypothesis import given, strategies as st
import networkx as nx

# Summary: 
# - Generate a random directed graph by drawing number of nodes and edges
# - Randomly select 2 nodes from the graph to pass as node1 and node2 
# - Draw a default value to return if no common ancestor
# - Check that return value is either the correct common ancestor or the default
# - Check that an exception is not raised for valid inputs
# - Check that node1 and node2 have a path to the common ancestor 
@given(st.data())
def test_networkx_lowest_common_ancestor(data):
    # Generate random directed graph
    num_nodes = data.draw(st.integers(min_value=2, max_value=100))
    num_edges = data.draw(st.integers(min_value=1, max_value=num_nodes*(num_nodes-1)//2))
    G = nx.gnm_random_graph(num_nodes, num_edges, directed=True) 
    
    # Randomly select 2 nodes and a default value
    node1, node2 = data.draw(st.permutations(list(G.nodes), 2))
    default_val = data.draw(st.none() | st.integers() | st.text())

    # Call function and check properties  
    lca = nx.lowest_common_ancestor(G, node1, node2, default=default_val)

    # Check return value is the lca or default
    if nx.has_path(G, node1, node2):  
        assert lca in nx.ancestors(G, node1) and lca in nx.ancestors(G, node2)
    else:
        assert lca == default_val
    
    # Check paths exist from lca to both nodes
    if lca is not default_val:
        assert nx.has_path(G, lca, node1) and nx.has_path(G, lca, node2)
# End program