from hypothesis import given, strategies as st
import networkx as nx

@given(st.data())
def test_find_cliques(data):
    # Prepare a realistic graph size limit for testing purposes
    max_nodes = 100

    # Randomly generate a graph and a list of nodes
    nodes = data.draw(st.lists(st.integers(min_value=0, max_value=max_nodes), min_size=1, max_size=max_nodes))
    edges = data.draw(st.sets(st.tuples(st.sampled_from(nodes), st.sampled_from(nodes))))
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
        
    # Randomly generate nodes to be in cliques
    clique_nodes = data.draw(st.lists(st.sampled_from(nodes), min_size=1, max_size=len(nodes)))

    # Test API function and properties
    try:
        cliques = nx.find_cliques(G, clique_nodes)
        
        assert isinstance(cliques, type(iter([])))
        
        for clique in cliques:
            assert set(clique_nodes).issubset(clique)
            for node in clique:
                # check if clique is maximal
                assert not any(set(clique).issubset(set(neighborhood)) for neighborhood in G.neighbors(node))

    except ValueError as ve:
        # If nodes are not a clique check if ValueError is raised
        assert not is_clique(G.subgraph(clique_nodes))

# Helper function to check if a subgraph is a clique
def is_clique(G):
    for node in G.nodes:
        neighbors = list(G.neighbors(node))
        for neighbor in neighbors:
            # if there is a node in G not connected to `node` return False
            if not set(neighbors).issubset(G.neighbors(neighbor)):
                return False
    return True