from hypothesis import given, strategies as st
from itertools import combinations
import networkx as nx

@given(st.lists(st.integers(min_value=1, max_value=500), min_size=1, max_size=500))
def test_networkx_find_cliques(nodes):
    # Create a graph from nodes
    G = nx.Graph()
    G.add_nodes_from(nodes)
    
    for edge in combinations(nodes, 2):
        if st.booleans(): 
            G.add_edge(*edge)

    # Get result from find_cliques
    result = nx.find_cliques(G)

    # Test that result is correct type
    assert isinstance(result, type(iter([]))), "Returned value is not an iterator"

    # Test that every returned list contains nodes that exist in the graph
    for clique in result:
        assert all(node in nodes for node in clique), "Returned clique contains node not present in graph"

    if nodes:    # if a clique of node(s) is provided
        result = nx.find_cliques(G, nodes)
        
        # Test that provided nodes exist in returned cliques
        for clique in result:
            assert all(node in clique for node in nodes), "Returned clique does not contain all provided nodes"
            
# End program