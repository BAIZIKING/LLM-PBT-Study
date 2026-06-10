from hypothesis import given, strategies as st
import networkx as nx

@given(st.integers(min_value=0, max_value=20), st.lists(st.integers(min_value=0, max_value=20), min_size=0, max_size=20, unique=True), st.randoms())
def test_find_cliques(num_of_nodes, nodes, seed):
    # Use the seed to create a predictable random Graph.
    seed.seed(0)
    G = nx.gnp_random_graph(num_of_nodes, 0.5, seed=seed)
    
    # Make sure the nodes are in the graph
    nodes = [node for node in nodes if node < num_of_nodes]

    try:
        cliques = nx.find_cliques(G, nodes)
    except ValueError:
        # If nodes is not a clique, the function should raise a ValueError
        assert not nx.is_clique(G.subgraph(nodes))
        return
    else:
        try:
            first = next(cliques)
        except StopIteration:
            # If the graph is empty, the cliques should also be empty
            assert num_of_nodes == 0
        else:
            # The cliques list should not be empty if the graph is not empty
            assert num_of_nodes > 0
        
    # Check that every node in 'nodes' appears in every clique in 'cliques'
    for clique in cliques:
        for node in nodes:
            assert node in clique
    
    # Check if it's a list of nodes in G
    for clique in cliques:
        for node in clique:
            assert node in G.nodes

# End program