from hypothesis import given, strategies as st
import networkx as nx

@given(st.lists(st.integers(min_value=0, max_value=100), min_size=4, max_size=10).map(set), st.integers(min_value=0, max_value=100))
def test_find_cliques_property_1(nodes, target):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    
    for i, node in enumerate(nodes):
        if i < len(nodes)-1:
            G.add_edge(node, list(nodes)[i+1])

    cliques = nx.find_cliques(G)
    
    # Property 1: The output successfully be converted into a list type
    try:
        cliques_list = list(cliques)
    except Exception:
        assert False, "Unable to convert cliques into a list"

    # Property 2: The type of elements in each clique will be the same as the type of the nodes in the graph
    for clique in cliques_list:
        for node in clique:
            assert isinstance(node, int), "Node in clique is not an integer"

    # Property 3: No clique should contain a node more than once
    for clique in cliques_list:
        assert len(set(clique)) == len(clique), "Clique contains duplicate nodes"

    # Property 4: Size of the largest maximal clique should not exceed the total number of nodes in the graph
    assert not any(len(clique) > len(nodes) for clique in cliques_list), "A Clique is larger than total nodes in the graph"

    # Property 5: If the 'nodes' parameter is given, then each clique in the output must contain all of those nodes
    target_cliques = [clique for clique in cliques_list if target in clique]
    assert all(target in clique for clique in target_cliques), "Not all cliques contain the target node"
