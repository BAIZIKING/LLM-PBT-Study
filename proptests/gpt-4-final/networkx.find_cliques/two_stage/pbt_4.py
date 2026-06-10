from hypothesis import given, strategies as st
import networkx as nx

@given(st.integers(min_value=2, max_value=10), st.data())
def test_find_cliques_property(num_nodes, data):
    # Generating a random graph using the "num_nodes"
    edges = st.lists(st.tuples(st.integers(min_value=0, max_value=num_nodes-1), 
                               st.integers(min_value=0, max_value=num_nodes-1)), 
                     min_size=num_nodes, max_size=num_nodes*(num_nodes-1)//2).\
                     map(set).\
                     filter(lambda s: len(s) == 2)
    G = nx.Graph(data.draw(edges))

    # Test 1: The function returns an iterator
    assert callable(getattr(nx.find_cliques(G), '__iter__', None))
    
    cliques = list(nx.find_cliques(G))
    
    # Test 2: Each clique contains distinct nodes.
    for clique in cliques:
        assert len(set(clique)) == len(clique)
    
    # Test 3: Each clique is a maximal clique
    for clique in cliques:
        for node in G.nodes():
            if node not in clique and all([(node in G.neighbors(n) or node == n) for n in clique]):
                assert False, f"Clique {clique} is not maximal"
    
    # Test 4: All maximal cliques are included in the output
    cliques_set = set([frozenset(c) for c in cliques])
    for clique in cliques:
        for node in G.nodes():
            if node not in clique:
                new_clique = clique + [node]
                if all([(n in G.neighbors(node) or n == node) for n in new_clique]):
                    assert frozenset(new_clique) in cliques_set
    
    # Test 5: Function returns cliques containing all nodes specified in input "nodes"
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=num_nodes-1), min_size=1, max_size=num_nodes))
    cliques_nodes = list(nx.find_cliques(G, nodes))
    for clique in cliques_nodes:
        for node in nodes:
            assert node in clique
    for clique in cliques:
        if all(n in clique for n in nodes):
            assert clique in cliques_nodes
# End program